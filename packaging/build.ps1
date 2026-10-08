# Build a Windows distribution of the Deployment Analyzer.
#
#   .\packaging\build.ps1            # builds dist\DeploymentAnalyzer-<version>-win64.zip
#
# Requires Python 3.10+ on PATH. A throw-away virtual environment is created
# in .venv-build so that only the runtime dependencies end up in the bundle.

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".venv-build")) {
    python -m venv .venv-build
}
$python = ".\.venv-build\Scripts\python.exe"
& $python -m pip install --upgrade pip --quiet
& $python -m pip install ".[build]" --quiet

$version = & $python -c "import deployment_analyzer; print(deployment_analyzer.__version__)"
Write-Host "Building DeploymentAnalyzer $version"

& $python -m PyInstaller --noconfirm --clean packaging\DeploymentAnalyzer.spec

$releaseDir = "dist\DeploymentAnalyzer-$version"
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
Move-Item "dist\DeploymentAnalyzer" $releaseDir
Copy-Item "README.md", "LICENSE", "CHANGELOG.md" $releaseDir

$zip = "dist\DeploymentAnalyzer-$version-win64.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path $releaseDir -DestinationPath $zip
Write-Host "Done: $zip"
