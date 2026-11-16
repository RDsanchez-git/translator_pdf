# A05-Q1: observacion no destructiva del host Windows / Hyper-V.
# Compatible con Windows PowerShell 5.1. NO crea, modifica ni arranca VMs.
# No certifica por si solo el aislamiento: siempre requiere revision humana.
[CmdletBinding()]
param(
    [string] $VMName = 'TST-STAB-LAB',
    [string] $OwnerRepoRoot = '.'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$blockers = New-Object 'System.Collections.Generic.List[string]'
$notes = New-Object 'System.Collections.Generic.List[string]'
$vmFound = $false
$hypervAvailable = $false
$vmState = $null
$adapterInfo = @()
$diskInfo = @()
$guestCopyEnabled = $null
$vmConfigPath = $null
$ownerRoot = $null

try {
    $resolved = Resolve-Path -LiteralPath $OwnerRepoRoot
    $ownerRoot = ([System.IO.Path]::GetFullPath($resolved.ProviderPath)).TrimEnd('\', '/')
} catch {
    $blockers.Add('OWNER_REPO_ROOT_NOT_FOUND')
}

$command = Get-Command -Name Get-VM -ErrorAction SilentlyContinue
if ($null -eq $command) {
    $blockers.Add('HYPERV_POWERSHELL_UNAVAILABLE')
    $notes.Add('No presuponer Hyper-V disponible; verificar edicion Windows y virtualizador.')
} else {
    $hypervAvailable = $true
    try {
        $vm = Get-VM -Name $VMName -ErrorAction Stop
        $vmFound = $true
        $vmState = [string] $vm.State
        $vmConfigPath = [string] $vm.Path
        if ($vmState -ne 'Off') {
            $blockers.Add('VM_NOT_OFF_FOR_INITIAL_HOST_REVIEW')
        }

        $adapters = @(Get-VMNetworkAdapter -VMName $VMName -ErrorAction Stop)
        foreach ($nic in $adapters) {
            $adapterInfo += [pscustomobject]@{
                name = [string] $nic.Name
                switch_name = [string] $nic.SwitchName
            }
            if (-not [string]::IsNullOrWhiteSpace([string] $nic.SwitchName)) {
                $blockers.Add('VM_NIC_ATTACHED_TO_SWITCH')
            }
        }

        $disks = @(Get-VMHardDiskDrive -VMName $VMName -ErrorAction Stop)
        if ($disks.Count -eq 0) {
            $blockers.Add('VM_HAS_NO_HARD_DISK')
        }
        foreach ($disk in $disks) {
            $diskPath = [string] $disk.Path
            $diskInfo += $diskPath
            if ([string]::IsNullOrWhiteSpace($diskPath)) {
                $blockers.Add('VM_DISK_PATH_MISSING')
            } elseif ($null -ne $ownerRoot) {
                $normalizedDisk = ([System.IO.Path]::GetFullPath($diskPath)).TrimEnd('\', '/')
                if ($normalizedDisk.Equals($ownerRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
                    $normalizedDisk.StartsWith(($ownerRoot + '\'), [System.StringComparison]::OrdinalIgnoreCase)) {
                    $blockers.Add('VM_DISK_INSIDE_OWNER_REPOSITORY')
                }
            }
        }

        $services = @(Get-VMIntegrationService -VMName $VMName -ErrorAction Stop)
        $fileCopy = @($services | Where-Object { $_.Name -eq 'Guest Service Interface' })
        if ($fileCopy.Count -ne 1) {
            $blockers.Add('GUEST_FILE_COPY_SERVICE_UNDETERMINED')
        } else {
            $guestCopyEnabled = [bool] $fileCopy[0].Enabled
            if ($guestCopyEnabled) {
                $blockers.Add('HYPERV_GUEST_FILE_COPY_ENABLED')
            }
        }
        $notes.Add('Comprobar manualmente Enhanced Session, montajes, portapapeles, agentes y acceso a credenciales.')
        $notes.Add('Comprobar en Linux guest: mountinfo, variables de entorno, usuario y red denegada.')
    } catch {
        if (-not $vmFound) {
            $blockers.Add('VM_NOT_FOUND_OR_ACCESS_DENIED')
        } else {
            $blockers.Add('HYPERV_HOST_INSPECTION_FAILED')
        }
        $notes.Add('Error de inspeccion: ' + $_.Exception.GetType().Name)
    }
}

$report = [ordered]@{
    purpose = 'A05_HYPERV_HOST_READ_ONLY_PRECHECK'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    vm_name = $VMName
    hyperv_cmdlet_available = $hypervAvailable
    vm_found = $vmFound
    vm_state = $vmState
    vm_configuration_path = $vmConfigPath
    network_adapters = @($adapterInfo)
    vm_hard_disk_paths = @($diskInfo)
    guest_service_interface_enabled = $guestCopyEnabled
    explicit_blockers = @($blockers | Select-Object -Unique)
    operator_review_required = $true
    host_isolation_verified = $false
    a06_authorized = $false
    result = if ($blockers.Count) { 'BLOCKED' } else { 'PRECHECK_ONLY_HUMAN_REVIEW_REQUIRED' }
    notes = @($notes)
}
$report | ConvertTo-Json -Depth 7
if ($blockers.Count) { exit 2 }
exit 0
