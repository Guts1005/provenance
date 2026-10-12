@echo off
title Provenance — Installer
cd /d "%~dp0"

echo ==========================================================
echo       PROVENANCE INDUSTRIAL CCTV PACKING SUITE
echo               Workstation Setup Wizard
echo ==========================================================
echo.
echo Requesting Administrator Privileges...

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0installer\Setup_Wizard.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Setup exited with code %ERRORLEVEL%.
    pause
)
