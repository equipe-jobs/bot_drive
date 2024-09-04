$exclude = @("venv", "driver_bot1.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "driver_bot1.zip" -Force