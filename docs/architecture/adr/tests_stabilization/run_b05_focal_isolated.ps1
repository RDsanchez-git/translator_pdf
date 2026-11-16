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
    [switch] $CheckB03Parser,
    [switch] $CheckB04Contracts,
    [switch] $CheckA03Boundaries,
    [switch] $CheckA03Sensitivity,
    [switch] $CheckForegroundSensitivity,
    [switch] $CheckCLIAdmissionSensitivity,
    [switch] $CheckG5Worker,
    [switch] $CheckG5WorkerSensitivity,
    [switch] $CheckC3T05Process,
    [switch] $CheckA05Safety,
    [switch] $PreflightA06,
    [switch] $CaptureProtectedPaths
)

# A-05 P6: hash only protected technical inputs. Never scan canonical scientific corpus.
function Write-ProtectedInventory {
    param([string] $CloneRoot, [string] $Output)
    $entries = New-Object 'System.Collections.Generic.List[string]'
    foreach ($relative in @("tests/fixtures", "tests/golden", "infra/db")) {
        $base = Join-Path $CloneRoot $relative
        if (-not (Test-Path -LiteralPath $base)) { continue }
        $items = @(Get-ChildItem -LiteralPath $base -Force -Recurse -ErrorAction Stop |
            Sort-Object FullName)
        foreach ($item in $items) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "STOP: protected tree contains a reparse point: $($item.FullName)"
            }
            if ($item.PSIsContainer) { continue }
            $rel = $item.FullName.Substring($CloneRoot.Length + 1).Replace('\', '/')
            $digest = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
            $entries.Add(("$rel" + [char]9 + $item.Length + [char]9 + $digest))
        }
    }
    [IO.File]::WriteAllLines($Output, $entries.ToArray(), ([Text.UTF8Encoding]::new($false)))
}

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ($PreflightA06 -and ($CaptureProtectedPaths -or $CheckA05Safety -or $CheckSensitivity -or $CheckB01B02 -or $CheckB01B02Sensitivity -or $CheckG3G5 -or $CheckG3G5Sensitivity -or $CheckB03Parser -or $CheckB04Contracts -or $CheckA03Boundaries -or $CheckA03Sensitivity -or $CheckForegroundSensitivity -or $CheckCLIAdmissionSensitivity -or $CheckG5Worker -or $CheckG5WorkerSensitivity -or $CheckC3T05Process)) {
    throw "STOP: A06 preflight is metadata-only and cannot be combined with test selections."
}
if ($CheckB01B02Sensitivity) {
    $CheckB01B02 = $true
}
if ($CheckG3G5Sensitivity) {
    $CheckG3G5 = $true
}
if ($CheckA03Sensitivity) {
    $CheckA03Boundaries = $true
}
if ($CheckG5WorkerSensitivity) {
    $CheckG5Worker = $true
}
if ($CheckForegroundSensitivity -and ($CheckA03Boundaries -or $CheckB04Contracts -or $CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: foreground sensitivity is a separate selection."
}
if ($CheckCLIAdmissionSensitivity -and ($CheckForegroundSensitivity -or $CheckA03Boundaries -or $CheckB04Contracts -or $CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: CLI admission sensitivity must run separately."
}
if ($CheckG5Worker -and ($CheckCLIAdmissionSensitivity -or $CheckForegroundSensitivity -or $CheckA03Boundaries -or $CheckB04Contracts -or $CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: G5 worker must run as a separate focal selection."
}
if ($CheckC3T05Process -and ($CheckG5Worker -or $CheckCLIAdmissionSensitivity -or $CheckForegroundSensitivity -or $CheckA03Boundaries -or $CheckB04Contracts -or $CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: C3/T05 process-boundary test must run separately."
}
if ($CheckA05Safety -and ($CheckC3T05Process -or $CheckG5Worker -or $CheckForegroundSensitivity -or $CheckCLIAdmissionSensitivity -or $CheckA03Boundaries -or $CheckB04Contracts -or $CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity -or $CheckB01B02Sensitivity -or $CheckG3G5Sensitivity -or $CheckA03Sensitivity -or $CheckG5WorkerSensitivity)) {
    throw "STOP: A05 safety checks must run alone without sensitivity probes."
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
if ($CheckB04Contracts -and ($CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: B04 technical contracts are a separate focal execution."
}
if ($CheckA03Boundaries -and ($CheckB04Contracts -or $CheckB03Parser -or $CheckG3G5 -or $CheckB01B02 -or $CheckSensitivity)) {
    throw "STOP: A03 parser/G3 boundary audit is a separate focal execution."
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

if ($PreflightA06) {
    # No pytest, no collection, no test imports or bodies in this mode.
    Write-ProtectedInventory -CloneRoot $copy -Output (Join-Path $reports "protected_before.tsv")
    # Windows PowerShell 5.1 strips nested quotes in native -c arguments.
    # Send literal Python source via stdin; no test imports or plugin loading.
    $pluginProbe = @'
import importlib.metadata as m
print("pytest=" + m.version("pytest"))
print("pytest_asyncio=" + m.version("pytest-asyncio"))
for entry in sorted(m.entry_points(group="pytest11"), key=lambda x: x.name):
    print("entrypoint=" + entry.name + "|" + entry.value)
'@
    $pluginProbe | & $python -I -B - 2>&1 |
        Out-File -FilePath (Join-Path $reports "plugin_entrypoints.txt") -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "STOP: installed pytest plugin metadata inspection failed" }
    & git -C $copy status --porcelain=v1 --untracked-files=all --ignored |
        Out-File -FilePath (Join-Path $reports "git_after.txt") -Encoding utf8
    if ($LASTEXITCODE -ne 0 -or @(Get-Content (Join-Path $reports "git_after.txt")).Count -ne 0) {
        throw "STOP: preflight altered the retained clone"
    }
    @(
        "source_sha=$revision"
        "mode=A06_PREFLIGHT_METADATA_ONLY"
        "pytest_bodies=NOT_RUN"
        "pytest_collection=NOT_RUN"
        "loaded_pytest_plugins=NOT_INSPECTED"
        "network_os_isolation=NOT_VERIFIED"
        "external_file_effects=NOT_VERIFIED"
        "protected_snapshot=protected_before.tsv"
        "plugin_metadata=plugin_entrypoints.txt"
        "clone=$copy"
        "reports=$reports"
    ) | Out-File -FilePath (Join-Path $reports "preflight_summary.txt") -Encoding utf8
    Write-Host "A06 preflight complete: no tests or pytest imports executed."
    Write-Host "Plugin metadata: $(Join-Path $reports 'plugin_entrypoints.txt')"
    Write-Host "Protected files: $(Join-Path $reports 'protected_before.tsv')"
    Write-Host "Reports retained: $reports"
    return
}
if ($CaptureProtectedPaths) {
    Write-ProtectedInventory -CloneRoot $copy -Output (Join-Path $reports "protected_before.tsv")
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
if ($CheckB04Contracts) {
    # B04: 3 mathematical/enum contracts + 5 legacy healing/telemetry contracts.
    $nodeids = @(
        "tests/test_pipeline_fidelity.py::TestMathProtectionContracts::test_math_placeholder_restoration_preserves_adjacency",
        "tests/test_pipeline_fidelity.py::TestMathProtectionContracts::test_mixed_inline_and_block_math",
        "tests/test_pipeline_fidelity.py::TestMathProtectionContracts::test_worker_passthrough_alignment",
        "tests/integration/test_healing_e2e_telemetry.py::test_healing_case_a_markdown_leakage",
        "tests/integration/test_healing_e2e_telemetry.py::test_healing_case_b_unbalanced_braces",
        "tests/integration/test_healing_e2e_telemetry.py::test_healing_case_c_math_truncation",
        "tests/integration/test_healing_e2e_telemetry.py::test_healing_rollback_guarantee_on_revalidation_failure",
        "tests/integration/test_healing_e2e_telemetry.py::test_healing_telemetry_aggregate_metrics"
    )
}
if ($CheckA03Boundaries) {
    # A03: existing G3-B3 pure result contracts + real synthetic PDF root.
    # All fixtures are in memory or tmp_path. No Docker, LLM or real corpus.
    $nodeids = @(
        "tests/integration/test_g3_b3_structured_result_contract.py",
        "tests/integration/test_verification_pipeline_connection.py"
    )
}
if ($CheckForegroundSensitivity) {
    # Two preexisting coordinator tests, NOT an OCR/G3/G5 physical E2E.
    $nodeids = @(
        "tests/integration/test_b03_foreground_pdf_product.py::test_foreground_fails_on_incomplete_g3_before_g5",
        "tests/integration/test_b03_foreground_pdf_product.py::test_foreground_fails_when_g5_did_not_publish"
    )
}
if ($CheckCLIAdmissionSensitivity) {
    # All eight existing inbox and CLI contracts. No full suite, provider, DB or Docker.
    $nodeids = @(
        "tests/integration/test_pdf_inbox_submission.py"
    )
}
if ($CheckG5Worker) {
    # Actual G5 daemon method, temporary WAL DB and faked compiler/renderer.
    $nodeids = @(
        "tests/integration/test_g5_assembler_worker_integration.py"
    )
}
if ($CheckC3T05Process) {
    # C3/T05: the abrupt exit belongs only to a child Python interpreter.
    # SQLite files live under the redirected TEMP directory of this clone.
    $nodeids = @(
        "tests/integration/test_c3_t05_process_boundary.py::test_t05_g3_staged_publication_crash_and_recovery_between_processes"
    )
}
if ($CheckA05Safety) {
    # A-05: 6 Tectonic + 3 legacy + 2 network opt-in safety cases.
    # No real Tectonic, provider, Docker or full technical suite.
    $nodeids = @(
        "tests/unit/test_tectonic_runner.py",
        "tests/integration/test_translation_structure.py::TestTranslationStructure::test_structural_integrity_against_golden_snapshot",
        "tests/integration/test_translation_technical.py::TestTranslationTechnical::test_latex_token_sets_and_balances",
        "tests/integration/test_translation_layer.py::TestTranslationLayerIntegration::test_translation_layer_flow",
        "tests/integration/test_embedding_smoke.py"
    )
}
$nodeids | Out-File -FilePath (Join-Path $reports "nodeids.txt") -Encoding utf8
$desired = @{
    "HOME" = $isolatedUserHome; "USERPROFILE" = $isolatedUserHome; "TMP" = $temp; "TEMP" = $temp
    "TMPDIR" = $temp; "XDG_CACHE_HOME" = $cache; "TIKTOKEN_CACHE_DIR" = $cache
    "PYTHONPATH" = $copy; "PYTHONDONTWRITEBYTECODE" = "1"
    "PYTHONNOUSERSITE" = "1"; "PYTEST_ADDOPTS" = ""; "PIP_NO_INDEX" = "1"
    "TRANSLATOR_PDF_RUN_LIVE_PROVIDER_TESTS" = "0"
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
$protectedSnapshotMatches = $true
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
            if ($exitCode -eq 0 -and $CheckG5WorkerSensitivity) {
                Write-Host "G5 worker: two contract mutations after three green baseline tests."
                [Environment]::SetEnvironmentVariable("TST_STAB_G5_WORKER_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_g5_worker_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "g5_worker_mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_G5_WORKER_OPT_IN", $null, "Process")
                }
            }
            if ($exitCode -eq 0 -and $CheckCLIAdmissionSensitivity) {
                Write-Host "CLI admission: two in-memory mutation probes after eight green tests."
                [Environment]::SetEnvironmentVariable("TST_STAB_CLI_ADMISSION_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_cli_admission_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "cli_admission_mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_CLI_ADMISSION_OPT_IN", $null, "Process")
                }
            }
            if ($exitCode -eq 0 -and $CheckForegroundSensitivity) {
                Write-Host "Foreground: two in-memory fail-closed mutations after green baseline."
                [Environment]::SetEnvironmentVariable("TST_STAB_FOREGROUND_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_foreground_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "foreground_mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_FOREGROUND_OPT_IN", $null, "Process")
                }
            }
            if ($exitCode -eq 0 -and $CheckA03Sensitivity) {
                Write-Host "A03 sensitivity: UTF-8 byte cap and extracted source loss, after green baseline."
                [Environment]::SetEnvironmentVariable("TST_STAB_A03_OPT_IN", "1", "Process")
                try {
                    & $python -B "docs/architecture/adr/tests_stabilization/probe_a03_sensitivity.py" --reports $reports *>&1 |
                        Out-File -FilePath (Join-Path $reports "a03_mutation_runner.log") -Encoding utf8
                    $sensitivityExitCode = $LASTEXITCODE
                } finally {
                    [Environment]::SetEnvironmentVariable("TST_STAB_A03_OPT_IN", $null, "Process")
                }
            }
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
    if ($CaptureProtectedPaths) {
        Write-ProtectedInventory -CloneRoot $copy -Output (Join-Path $reports "protected_after.tsv")
        $beforeDigest = (Get-FileHash -LiteralPath (Join-Path $reports "protected_before.tsv") -Algorithm SHA256).Hash
        $afterDigest = (Get-FileHash -LiteralPath (Join-Path $reports "protected_after.tsv") -Algorithm SHA256).Hash
        $protectedSnapshotMatches = ($beforeDigest -eq $afterDigest)
        if (-not $protectedSnapshotMatches) {
            "Protected paths changed: compare protected_before.tsv and protected_after.tsv" |
                Out-File (Join-Path $reports "protected_changes.txt") -Encoding utf8
        } else {
            [IO.File]::WriteAllText((Join-Path $reports "protected_changes.txt"), "")
        }
    }
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
        "b04_contracts_requested=$([bool]$CheckB04Contracts)"
        "a03_boundaries_requested=$([bool]$CheckA03Boundaries)"
        "a03_sensitivity_requested=$([bool]$CheckA03Sensitivity)"
        "foreground_sensitivity_requested=$([bool]$CheckForegroundSensitivity)"
        "cli_admission_sensitivity_requested=$([bool]$CheckCLIAdmissionSensitivity)"
        "g5_worker_requested=$([bool]$CheckG5Worker)"
        "g5_worker_sensitivity_requested=$([bool]$CheckG5WorkerSensitivity)"
        "c3_t05_process_requested=$([bool]$CheckC3T05Process)"
        "a05_safety_requested=$([bool]$CheckA05Safety)"
        "protected_inventory_requested=$([bool]$CaptureProtectedPaths)"
        "protected_inventory_unchanged=$protectedSnapshotMatches"
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
if ($CheckSensitivity -or $CheckB01B02Sensitivity -or $CheckG3G5Sensitivity -or $CheckA03Sensitivity -or $CheckForegroundSensitivity -or $CheckCLIAdmissionSensitivity -or $CheckG5WorkerSensitivity) {
    Write-Host "Sensitivity exit code: $sensitivityExitCode"
    $mutationFile = if ($CheckG5WorkerSensitivity) {
        "g5_worker_mutation_summary.json"
    } elseif ($CheckCLIAdmissionSensitivity) {
        "cli_admission_mutation_summary.json"
    } elseif ($CheckForegroundSensitivity) {
        "foreground_mutation_summary.json"
    } elseif ($CheckA03Sensitivity) {
        "a03_mutation_summary.json"
    } elseif ($CheckG3G5Sensitivity) {
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
if ($CaptureProtectedPaths -and -not $protectedSnapshotMatches) { exit 5 }
# A-05 requires the isolated checkout to remain Git-clean after these tests.
if ($CheckA05Safety -and @(Get-Content -LiteralPath (Join-Path $reports "status_changes.txt")).Count -ne 0) {
    Write-Host "STOP: A05 tests changed the isolated Git checkout. Inspect status_changes.txt."
    exit 4
}
if (($CheckSensitivity -or $CheckB01B02Sensitivity -or $CheckG3G5Sensitivity -or $CheckA03Sensitivity -or $CheckForegroundSensitivity -or $CheckCLIAdmissionSensitivity -or $CheckG5WorkerSensitivity) -and $sensitivityExitCode -ne 0) { exit 3 }
exit 0