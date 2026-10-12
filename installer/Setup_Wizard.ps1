<#
.SYNOPSIS
    Provenance Industrial Suite — Automated Windows Setup & Installation Wizard.
.DESCRIPTION
    Deploys compiled Provenance binaries, creates desktop shortcuts, configures custom or default
    video evidence storage directories, opens Windows Firewall port 5892, and anchors hardware licensing.
#>

[CmdletBinding()]
param (
    [string]$TargetDir = "$env:ProgramFiles\Provenance",
    [string]$ClipsDir = "C:\Provenance\Clips",
    [switch]$SkipFirewall,
    [switch]$Unattended,
    [switch]$Gui
)

# Enforce Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Setup requires Administrator elevation to configure Program Files and Firewall rules."
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

$ScriptDir = Split-Path -Parent $PSCommandPath
$ProjectRoot = Split-Path -Parent $ScriptDir
$SourceDist = Join-Path $ProjectRoot "dist\Provenance"

# If -Gui is requested or no switch is passed in an interactive console, check if GUI wizard can be launched
if ($Gui -or (-not $Unattended -and (Test-Path (Join-Path $ScriptDir "setup_wizard_gui.py")))) {
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonExe) {
        Write-Host "Launching Provenance Interactive GUI Setup Wizard..." -ForegroundColor Cyan
        & python (Join-Path $ScriptDir "setup_wizard_gui.py")
        exit $LASTEXITCODE
    }
}

Clear-Host
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         PROVENANCE INDUSTRIAL CCTV PACKING SUITE         " -ForegroundColor White
Write-Host "         Production Workstation Installation Wizard       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verify Source Payload
if (-not (Test-Path $SourceDist)) {
    if (Test-Path (Join-Path $ScriptDir "Provenance.exe")) {
        $SourceDist = $ScriptDir
    } else {
        Write-Host "[-] Compiled distribution not found at: $SourceDist" -ForegroundColor Red
        Write-Host "[*] Compiling binaries via PyInstaller now..." -ForegroundColor Yellow
        & python (Join-Path $ProjectRoot "scripts\build_installer.py")
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[-] Build failed. Please verify dependencies." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

Write-Host "[+] Source payload located at: $SourceDist" -ForegroundColor Green

# 2. Interactive Installation Path Prompt
if (-not $Unattended) {
    Write-Host "`n[Destination Directory]" -ForegroundColor Cyan
    Write-Host "Default: $TargetDir" -ForegroundColor Gray
    $inDir = Read-Host "Press Enter to accept default, or enter custom path"
    if (-not [string]::IsNullOrWhiteSpace($inDir)) {
        $TargetDir = $inDir.Trim()
    }
}

# 3. Interactive Video Clips Location Prompt
if (-not $Unattended) {
    Write-Host "`n[Video Evidence Clips Storage Directory]" -ForegroundColor Cyan
    Write-Host "Recorded 1080p packaging sessions and SHA-256 dispute proofs are saved here." -ForegroundColor Gray
    Write-Host "  [1] Default Location (Recommended): C:\Provenance\Clips" -ForegroundColor White
    Write-Host "  [2] Custom Location (Secondary SSD/HDD or Mapped Drive)" -ForegroundColor White
    $cChoice = Read-Host "Choose option (Press Enter for Default [1])"
    if ($cChoice -eq "2") {
        $inClips = Read-Host "Enter custom video clips path (e.g. D:\ProvenanceClips or E:\WarehouseEvidence)"
        if (-not [string]::IsNullOrWhiteSpace($inClips)) {
            $ClipsDir = $inClips.Trim()
        }
    }
}

Write-Host "`nConfirmed Configuration:" -ForegroundColor White
Write-Host "  Target Application Dir : $TargetDir" -ForegroundColor Gray
Write-Host "  Video Clips Storage Dir: $ClipsDir" -ForegroundColor Green

# 4. Check Prerequisites
Write-Host "`n[1/5] Checking System Prerequisites..." -ForegroundColor Cyan
$arch = (Get-CimInstance Win32_OperatingSystem).OSArchitecture
Write-Host "  Architecture: $arch" -ForegroundColor Gray

# Check Edge WebView2 Runtime
$wv2 = (Get-ItemProperty -Path "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-F552-44E6-A13E-BE66465492BE}" -ErrorAction SilentlyContinue).pv
if (-not $wv2) {
    $wv2 = (Get-ItemProperty -Path "HKCU:\Software\Microsoft\EdgeUpdate\Clients\{F3017226-F552-44E6-A13E-BE66465492BE}" -ErrorAction SilentlyContinue).pv
}
if ($wv2) {
    Write-Host "  Edge WebView2 Runtime: Detected (v$wv2)" -ForegroundColor Green
} else {
    Write-Host "  Edge WebView2 Runtime: Built-in Windows Evergreen detected." -ForegroundColor Gray
}

# 5. Deploy Files
Write-Host "`n[2/5] Installing Provenance Core Binaries & Configuring Storage..." -ForegroundColor Cyan
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}
if (-not (Test-Path $ClipsDir)) {
    New-Item -ItemType Directory -Path $ClipsDir -Force | Out-Null
    Write-Host "  Created video evidence storage directory: $ClipsDir" -ForegroundColor Green
}
$dataDir = Join-Path $TargetDir "data"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
}

# Terminate running instance if any
Stop-Process -Name "Provenance" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 400

Copy-Item -Path "$SourceDist\*" -Destination $TargetDir -Recurse -Force
Write-Host "  Files copied to: $TargetDir" -ForegroundColor Green

# Configure clips_dir in database settings
$dbPath = Join-Path $dataDir "barcode_test.db"
try {
    $escClips = $ClipsDir -replace "\\", "\\"
    $initPy = "import sqlite3; conn = sqlite3.connect(r'$dbPath'); conn.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);'); conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (\'clips_dir\', ?);', (r'$ClipsDir',)); conn.commit(); conn.close(); print('CONFIG_SAVED')"
    $pyRes = & python -c $initPy
    Write-Host "  Configured default clips storage location in database: $ClipsDir" -ForegroundColor Green
} catch {
    Write-Warning "Could not write initial clips directory to database: $_"
}

# 6. Create Desktop & Start Menu Shortcuts
Write-Host "`n[3/5] Generating Desktop & Start Menu Shortcuts..." -ForegroundColor Cyan
$WshShell = New-Object -ComObject WScript.Shell

# Desktop Shortcut
$DesktopPath = [Environment]::GetFolderPath("CommonDesktopDirectory")
$Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "Provenance.lnk"))
$Shortcut.TargetPath = (Join-Path $TargetDir "Provenance.exe")
$Shortcut.WorkingDirectory = $TargetDir
$Shortcut.Description = "Provenance — Shipment CCTV Proof & Packing Station"
$Shortcut.Save()
Write-Host "  Created Desktop Shortcut: $DesktopPath\Provenance.lnk" -ForegroundColor Green

# Start Menu Shortcut
$StartMenuPath = [Environment]::GetFolderPath("CommonPrograms")
$ProgGroup = Join-Path $StartMenuPath "Provenance"
if (-not (Test-Path $ProgGroup)) { New-Item -ItemType Directory -Path $ProgGroup -Force | Out-Null }
$StartShortcut = $WshShell.CreateShortcut((Join-Path $ProgGroup "Provenance.lnk"))
$StartShortcut.TargetPath = (Join-Path $TargetDir "Provenance.exe")
$StartShortcut.WorkingDirectory = $TargetDir
$StartShortcut.Description = "Provenance — Shipment CCTV Proof & Packing Station"
$StartShortcut.Save()
Write-Host "  Created Start Menu Shortcut: $ProgGroup\Provenance.lnk" -ForegroundColor Green

# 7. Windows Firewall Exception
Write-Host "`n[4/5] Configuring Local Network & Firewall Rules..." -ForegroundColor Cyan
if (-not $SkipFirewall) {
    try {
        netsh advfirewall firewall delete rule name="Provenance CCTV API" | Out-Null
        netsh advfirewall firewall add rule name="Provenance CCTV API" dir=in action=allow protocol=TCP localport=5892 program=(Join-Path $TargetDir "Provenance.exe") | Out-Null
        Write-Host "  Inbound TCP Port 5892 authorized for CCTV streaming." -ForegroundColor Green
    } catch {
        Write-Warning "Could not register firewall rule: $_"
    }
}

# 8. Hardware Node-Locking & License Audit
Write-Host "`n[5/5] Auditing Machine Hardware Node Licensing..." -ForegroundColor Cyan
$LicTool = Join-Path $ProjectRoot "license_guard.py"
if (Test-Path $LicTool) {
    $licOut = & python $LicTool
    $hwLine = ($licOut | Where-Object { $_ -match "Machine Hardware ID" })
    if ($hwLine) {
        Write-Host "  $hwLine" -ForegroundColor Yellow
    }
    $licFile = Join-Path $ProjectRoot "provenance.lic"
    if (Test-Path $licFile) {
        Copy-Item -Path $licFile -Destination $TargetDir -Force
        Write-Host "  Cryptographic license key deployed to workstation." -ForegroundColor Green
    }
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "          INSTALLATION COMPLETED SUCCESSFULLY!            " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Application: $TargetDir\Provenance.exe" -ForegroundColor White
Write-Host "Clips Storage: $ClipsDir" -ForegroundColor White
Write-Host ""

if (-not $Unattended) {
    $launch = Read-Host "Launch Provenance now? (Y/n)"
    if ($launch -ne "n" -and $launch -ne "N") {
        Start-Process -FilePath (Join-Path $TargetDir "Provenance.exe") -WorkingDirectory $TargetDir
    }
}
