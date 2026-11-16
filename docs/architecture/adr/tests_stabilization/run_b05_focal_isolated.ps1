# B05 focal validator. Windows PowerShell 5.1; no Docker or full suite.
# Copies only committed files to a retained independent Git clone.
[CmdletBinding()]
param([string] $RepoRoot = ".")

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath $RepoRoot).ProviderPath
if (-not (Test-Path -LiteralPath (Join-Path $root "pyproject.toml"))) {
    throw "STOP: root lacks pyproject.toml"
}
$python = (Get-Command python -ErrorAction Stop).Source
$branch = (& git -C $root branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $branch -ne "tests_stabilization") {
    throw "STOP: select tests_stabilization before running."
}
$revision = (& git -C $root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $revision -notmatch "^[0-9a-f]{40}$") {
    throw "STOP: invalid Git SHA"
}

$scratch = Join-Path ([IO.Path]::GetTempPath()) ("tst-stab-b05-" + [Guid]::NewGuid().ToString("N"))
$copy = Join-Path $scratch "repo"
$reports = Join-Path $scratch "reports"
$temp = Join-Path $scratch "temp"
$home = Join-Path $scratch "home"
$cache = Join-Path $scratch "cache"
foreach ($dir in @($scratch, $reports, $temp, $home, $cache)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}
Write-Host "Sandbox directory (retain): $scratch"
Write-Host "Pinned source SHA: $revision"
& git clone --no-hardlinks --no-checkout -- $root $copy
if ($LASTEXITCODE -ne 0) { throw "STOP: clone failed" }
& git -C $copy checkout --detach $revision
if ($LASTEXITCODE -ne 0) { throw "STOP: checkout failed" }
& git -C $copy remote remove origin
if ($LASTEXITCODE -ne 0) { throw "STOP: remote removal failed" }
$actual = (& git -C $copy rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actual -ne $revision) {
    throw "STOP: checkout revision mismatch"
}
& git -C $copy status --porcelain=v1 --untracked-files=all --ignored |
    Out-File -FilePath (Join-Path $reports "git_before.txt") -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "STOP: git inventory failed" }
if (@(Get-Content (Join-Path $reports "git_before.txt")).Count -ne 0) {
    throw "STOP: clone is dirty before pytest; inspect git_before.txt"
}

$nodeids = @(
    "tests/integration/test_recovery_flow.py::TestRecoveryAndResumeEndToEnd::test_complete_crash_recovery_and_resume_lifecycle",
    "tests/integration/test_e2e_walking_skeleton.py::TestLegacyDispatcherCache::test_legacy_cache_hit_observed_across_two_dispatches",
    "tests/integration/test_real_e2e.py::TestRealE2EFinOps::test_mocked_pipeline_result_exposes_finops_fields",
    "tests/integration/test_pipeline_orchestration.py::TestPipelineOrchestration::test_legacy_orchestrator_handoff_with_mocked_parser"
)
$nodeids | Out-File -FilePath (Join-Path $reports "nodeids.txt") -Encoding utf8
$desired = @{
    "HOME" = $home; "USERPROFILE" = $home; "TMP" = $temp; "TEMP" = $temp
    "TMPDIR" = $temp; "XDG_CACHE_HOME" = $cache; "TIKTOKEN_CACHE_DIR" = $cache
    "PYTHONPATH" = $copy; "PYTHONDONTWRITEBYTECODE" = "1"
    "PYTHONNOUSERSITE" = "1"; "PYTEST_ADDOPTS" = ""; "PIP_NO_INDEX" = "1"
}
$secretPattern = "(?i)(TOKEN|SECRET|PASSWORD|PASSWD|API_KEY|ACCESS_KEY|PRIVATE_KEY|CREDENTIAL|^AWS_|^AZURE_|^GCP_|^OPENAI_|^GEMINI_|^GROQ_|^HF_)"
$original = @{}
foreach ($entry in @(Get-ChildItem Env:)) {
    if ($desired.ContainsKey($entry.Name) -or $entry.Name -match $secretPattern) {
        $original[$entry.Name] = $entry.Value
    }
}
$exitCode = 99
try {
    foreach ($key in $original.Keys) {
        [Environment]::SetEnvironmentVariable($key, $null, "Process")
    }
    foreach ($key in $desired.Keys) {
        [Environment]::SetEnvironmentVariable($key, $desired[$key], "Process")
    }
    Push-Location $copy
    try {
        & $python --version 2>&1 | Out-File (Join-Path $reports "python_version.txt") -Encoding utf8
        & $python -m pytest --version 2>&1 | Out-File (Join-Path $reports "pytest_version.txt") -Encoding utf8
        $savedAction = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            & $python -B -m pytest -q -ra --no-header -o "addopts=" -p "no:cacheprovider" --basetemp $temp $nodeids *>&1 |
                Out-File -FilePath (Join-Path $reports "pytest_focal.log") -Encoding utf8
            $exitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $savedAction
        }
    } finally {
        Pop-Location
    }
} finally {
    foreach ($key in $desired.Keys) {
        [Environment]::SetEnvironmentVariable($key, $null, "Process")
    }
    foreach ($key in $original.Keys) {
        [Environment]::SetEnvironmentVariable($key, $original[$key], "Process")
    }
    & git -C $copy status --porcelain=v1 --untracked-files=all --ignored |
        Out-File -FilePath (Join-Path $reports "git_after.txt") -Encoding utf8
    Compare-Object -ReferenceObject @(Get-Content (Join-Path $reports "git_before.txt")) -DifferenceObject @(Get-Content (Join-Path $reports "git_after.txt")) |
        Out-File -FilePath (Join-Path $reports "status_changes.txt") -Encoding utf8
    @(
        "source_sha=$revision"
        "pytest_exit_code=$exitCode"
        "clone=$copy"
        "reports=$reports"
        "docker_used=false"
        "no_OS_level_sandbox_claim=true"
    ) | Out-File -FilePath (Join-Path $reports "summary.txt") -Encoding utf8
}
Write-Host "pytest exit code: $exitCode"
Write-Host "pytest log: $(Join-Path $reports 'pytest_focal.log')"
Write-Host "Git diff inventory: $(Join-Path $reports 'status_changes.txt')"
Write-Host "No files were cleaned up; retain this clone and reports."
if ($exitCode -ne 0) { exit 2 }
exit 0
