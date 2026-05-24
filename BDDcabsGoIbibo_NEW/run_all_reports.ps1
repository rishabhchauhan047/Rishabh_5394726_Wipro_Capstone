$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
& ".\.venv\Scripts\python.exe" ".\scripts\run_all_reports.py"
