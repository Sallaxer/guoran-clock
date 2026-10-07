param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Push-Location $repoRoot
try {
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    & $Python -m PyInstaller --noconfirm --onefile --windowed --name GuoranClock-2.4.0 --icon "$repoRoot/ui/clock.ico" --add-data "$repoRoot/ui;ui" --distpath "$repoRoot/releases" --workpath "$repoRoot/build" --specpath "$repoRoot/build" --collect-all bleak --collect-submodules winrt "$repoRoot/guoran_desktop.py"
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    Get-FileHash "$repoRoot/releases/GuoranClock-2.4.0.exe" -Algorithm SHA256
} finally { Pop-Location }
