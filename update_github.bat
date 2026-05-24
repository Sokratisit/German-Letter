@echo off
setlocal

cd /d "%~dp0"

set /p COMMIT_MESSAGE=Commit message: 
if "%COMMIT_MESSAGE%"=="" (
    echo Commit cancelled: no message provided.
    exit /b 1
)

git status
git add .
git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 exit /b %errorlevel%

git push
exit /b %errorlevel%
