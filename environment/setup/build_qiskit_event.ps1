# E3 / Phase 2 (Windows) - build Qiskit-under-test FROM SOURCE for one revision.
# Usage:  .\environment\setup\build_qiskit_event.ps1 -Sha 2.4.2 -EventEnvId smoke-2_4_2
param(
    [Parameter(Mandatory=$true)][string]$Sha,
    [Parameter(Mandatory=$true)][string]$EventEnvId,
    [switch]$Force
)
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
Set-Location $RepoRoot

$Work = "environment\_builds\$EventEnvId"
$Lock = "environment\events\$EventEnvId.lock"

if ((Test-Path $Lock) -and -not $Force) {
    Write-Host ">> $Lock already exists; skipping rebuild (use -Force to rebuild)."
    exit 0
}

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "Rust toolchain (cargo) not found - required to build Qiskit from source. See SETUP_WINDOWS.md."
    exit 2
}
New-Item -ItemType Directory -Force -Path $Work, "environment\events" | Out-Null

if (-not (Test-Path "$Work\qiskit")) { git clone https://github.com/Qiskit/qiskit "$Work\qiskit" }
git -C "$Work\qiskit" fetch --all --tags --quiet
git -C "$Work\qiskit" checkout --quiet $Sha
$Resolved = (git -C "$Work\qiskit" rev-parse HEAD).Trim()

py -3.11 -m venv "$Work\venv"
# Use the venv's python.exe DIRECTLY (do not Activate.ps1 — that would leave the per-event venv
# active in the caller's shell; keep the caller on .venv-anchor).
$VenvPy = "$Work\venv\Scripts\python.exe"
& $VenvPy -m pip install --upgrade "pip>=19" "setuptools-rust>=1.9" wheel
Write-Host ">> Building Qiskit @ $Resolved from source"
rustc --version
& $VenvPy -m pip install "$Work\qiskit"

$py = @"
import json, platform, qiskit
print(json.dumps({
  'event_environment_id': '$EventEnvId',
  'requested': '$Sha',
  'resolved_sha': '$Resolved',
  'qiskit_version': qiskit.__version__,
  'python': platform.python_version(),
  'platform': platform.platform(),
}, indent=2))
"@
& $VenvPy -c $py | Out-File -Encoding ascii $Lock
Write-Host ">> Recorded $Lock"
