@echo off
setlocal
cd /d "%~dp0"

set "TARGET_URL=https://sokratis.pythonanywhere.com/generate"
set "OUTPUT_FILE=%~dp0testbrief.pdf"

curl.exe -X POST "%TARGET_URL%" -F "sender_last_name=Mustermann" -F "recipient_last_name=Beispiel" -F "subject=Testbrief" -F "subject_separator=: " -F "opening=Sehr geehrte Damen und Herren," -F "body=Dies ist ein Test." -F "closing=Mit freundlichen Grüßen" -F "place=Berlin" -F "place_separator=, " -F "date_iso=2026-05-24" -F "filename_addressee=Beispiel" --output "%OUTPUT_FILE%"

if errorlevel 1 (
    echo Request failed.
    pause
    exit /b %errorlevel%
)

echo Saved PDF to:
echo %OUTPUT_FILE%
pause
