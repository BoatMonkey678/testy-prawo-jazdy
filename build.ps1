pyinstaller testy-prawo-jazdy.spec

Copy-Item -Recurse -Force "static" "dist\static"
Copy-Item -Recurse -Force "templates" "dist\templates"
Copy-Item -Recurse -Force "resources" "dist\resources"
Copy-Item -Recurse -Force "config.ini" "dist\config.ini"

Write-Host ""
Write-Host "Build complete."
Write-Host "Output: dist\testy-prawo-jazdy.exe"