Set-Location "E:\dev\electricity-pipeline"

$fecha = Get-Date -Format "yyyyMMdd"
$logFile = "logs\pipeline_$fecha.log"

& "C:\Users\Borja\.local\bin\uv.exe" run python scripts\run_pipeline.py *>> $logFile