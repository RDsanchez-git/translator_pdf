# Focused stabilization validator. Windows PowerShell 5.1; no Docker or full suite.
# Copies only committed files to a retained independent Git clone.
[CmdletBinding()]
param(
    [string] $RepoRoot = ".",
    [switch] $CheckSensitivity,
    [switch] $CheckB01B02,
    [switch] $CheckB01B02Sensitivity,
    [switch] $CheckG3G5,
    [switch] $CheckG3G5Sensitivity,
    [switch] $CheckB03Parser
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ($CheckB01B02Sensitivity) {
    $CheckB01B02 = $true
}
if ($CheckG3G5Sensitivity) {
    $CheckG3G5 = $true
}
if ($CheckB01B02 -and $CheckSensitivity) {
    throw "STOP: B01/B02 selection and B05 sensitivity are separate controlled runs."
}
if ($CheckG3G5 -and ($CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: G3/G5 baseline is an independent selection; do not combine runner modes."
}
if ($CheckB03Parser -and ($CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: B03 parser contract is a separate focal execution."
}
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
$isolatedUserHome = Join-Path $scratch "home"
$cache = Join-Path $scratch "cache"
foreach ($dir in @($scratch, $reports, $temp, $isolatedUserHome, $cache)) {
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
if ($CheckB01B02) {
    $nodeids = @(
        "tests/integration/test_golden_parser.py::test_production_parser_preserves_known_text_from_disposable_pdf",
        "tests/integration/test_chunker_snapshot.py::test_semantic_chunker_preserves_members_policy_and_source_exactly",
        "tests/integration/test_chunker_snapshot.py::test_semantic_chunker_rejects_lost_member_in_manifest",
        "tests/integration/test_chunker_snapshot.py::test_semantic_chunker_rejects_source_whitespace_mutation"
    )
}
if ($CheckG3G5) {
    # A02/A03/B06 focal: 2 W06 + 2 G3 publication + 2 G5 guards
    # plus 3 parametrized G5 recovery phases. All in tmp_path/in-memory SQLite.
    $nodeids = @(
        "tests/integration/test_w06_g3_uncertain_effect_offline.py::test_w06_lost_reply_is_quarantined_without_second_provider_call",
        "tests/integration/test_w06_g3_uncertain_effect_offline.py::test_w06_restart_never_reinitializes_provider_for_unknown",
        "tests/integration/test_g3_b4_3b_publication_recovery.py::test_completed_with_no_publication_fails_closed",
        "tests/integration/test_g3_b4_3b_publication_recovery.py::test_corrupt_projection_never_advances_fsm",
        "tests/integration/test_g5_assembler_lease_recovery.py::test_wrong_epoch_and_wrong_leader_cannot_recover",
        "tests/integration/test_g5_assembler_lease_recovery.py::test_expired_lease_old_worker_cannot_publish_even_without_takeover",
        "tests/integration/test_g5_assembler_lease_recovery.py::test_recovery_fences_old_owner_and_new_owner_completes"
    )
}
if ($CheckB03Parser) {
    $nodeids = @(
        "tests/integration/test_real_parser_pipeline.py::test_real_parser_repeatable_ids_and_text_across_two_temporary_pages"
    )
}
$nodeids | Out-File -FilePath (Join-Path $reports "nodeids.txt") -Encoding utf8
$desired = @{
    "HOME" = $isolatedUserHome; "USERPROFILE" = $isolatedUserHome; "TMP" = $temp; "TEMP" = $temp
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
$sensitivityExitCode = -1
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
            if ($exitCode -eq 0 -and $CheckB01B02Sensitivity) {
                Write-Host "B01/B02 sensitivity: two in-memory SUT mutations."
                [Environment]::SetEnvironmentVariable("TST_STAB_B01B02_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_b01b02_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "b01b02_mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_B01B02_OPT_IN", $null, "Process")
                }
            }
            if ($exitCode -eq 0 -and $CheckG3G5Sensitivity) {
                Write-Host "G3/G5 sensitivity: three in-memory SUT mutations after green baseline."
                [Environment]::SetEnvironmentVariable("TST_STAB_G3G5_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_g3g5_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "g3g5_mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_G3G5_OPT_IN", $null, "Process")
                }
            }
            if ($exitCode -eq 0 -and $CheckSensitivity) {
                Write-Host "B05 sensitivity: two in-memory SUT mutations in the cloned workspace."
                [Environment]::SetEnvironmentVariable("TST_STAB_SENSITIVITY_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_b05_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_SENSITIVITY_OPT_IN", $null, "Process")
                }
            }
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
    # Compare-Object in Windows PowerShell 5.1 does not accept empty arrays.
    $beforeStatus = @(Get-Content -LiteralPath (Join-Path $reports "git_before.txt"))
    $afterStatus = @(Get-Content -LiteralPath (Join-Path $reports "git_after.txt"))
    $deltaPath = Join-Path $reports "status_changes.txt"
    if ($beforeStatus.Count -eq 0 -and $afterStatus.Count -eq 0) {
        [IO.File]::WriteAllText($deltaPath, "")
    } elseif ($beforeStatus.Count -eq 0) {
        $afterStatus | ForEach-Object { "ADDED: $_" } |
            Out-File -FilePath $deltaPath -Encoding utf8
    } elseif ($afterStatus.Count -eq 0) {
        $beforeStatus | ForEach-Object { "REMOVED: $_" } |
            Out-File -FilePath $deltaPath -Encoding utf8
    } else {
        Compare-Object -ReferenceObject $beforeStatus -DifferenceObject $afterStatus |
            Out-File -FilePath $deltaPath -Encoding utf8
    }
    @(
        "source_sha=$revision"
        "pytest_exit_code=$exitCode"
        "b01_b02_requested=$([bool]$CheckB01B02)"
        "g3_g5_requested=$([bool]$CheckG3G5)"
        "b03_parser_requested=$([bool]$CheckB03Parser)"
        "g3_g5_sensitivity_requested=$([bool]$CheckG3G5Sensitivity)"
        "b01_b02_sensitivity_requested=$([bool]$CheckB01B02Sensitivity)"
        "sensitivity_requested=$([bool]$CheckSensitivity)"
        "sensitivity_exit_code=$sensitivityExitCode"
        "clone=$copy"
        "reports=$reports"
        "docker_used=false"
        "no_OS_level_sandbox_claim=true"
    ) | Out-File -FilePath (Join-Path $reports "summary.txt") -Encoding utf8
}
Write-Host "pytest exit code: $exitCode"
if ($CheckSensitivity -or $CheckB01B02Sensitivity -or $CheckG3G5Sensitivity) {
    Write-Host "Sensitivity exit code: $sensitivityExitCode"
    $mutationFile = if ($CheckG3G5Sensitivity) {
        "g3g5_mutation_summary.json"
    } elseif ($CheckB01B02Sensitivity) {
        "b01b02_mutation_summary.json"
    } else {
        "mutation_summary.json"
    }
    Write-Host "Sensitivity report: $(Join-Path $reports $mutationFile)"
}
Write-Host "pytest log: $(Join-Path $reports 'pytest_focal.log')"
Write-Host "Git diff inventory: $(Join-Path $reports 'status_changes.txt')"
Write-Host "No files were cleaned up; retain this clone and reports."
if ($exitCode -ne 0) { exit 2 }
if (($CheckSensitivity -or $CheckB01B02Sensitivity -or $CheckG3G5Sensitivity) -and $sensitivityExitCode -ne 0) { exit 3 }
exit 0