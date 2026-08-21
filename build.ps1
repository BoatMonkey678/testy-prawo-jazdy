pyinstaller driver-license.spec

Copy-Item -Recurse -Force "static" "dist\static"
Copy-Item -Recurse -Force "templates" "dist\templates"

Write-Host ""
Write-Host "Build complete."
Write-Host "Output: dist\driver-license.exe"