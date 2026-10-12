# Terminate running Provenance processes
Stop-Process -Name "Provenance" -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 600

# Grant Users full control on C:\Program Files\Provenance so future file syncs and in-place updates never hit access denied
& icacls "C:\Program Files\Provenance" /grant "BUILTIN\Users:(OI)(CI)F" /T /Q

# Copy updated distribution to Program Files
Copy-Item -Path "C:\Users\sharv\barcode-test\dist\Provenance\*" -Destination "C:\Program Files\Provenance" -Recurse -Force

# Relaunch Provenance
Start-Process "C:\Program Files\Provenance\Provenance.exe"
