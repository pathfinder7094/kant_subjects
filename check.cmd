@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "FAILED=0"

call :run "check index" "uv run --frozen python main.py check index"
call :run "run index" "uv run --frozen python main.py run index"
call :run "check answer" "uv run --frozen python main.py check answer"
call :run "check evaluate" "uv run --frozen python main.py check evaluate"
call :run "run answer --live" "uv run --frozen python main.py run answer --live"
call :run "run evaluate --live" "uv run --frozen python main.py run evaluate --live"

if "!FAILED!"=="1" (
    echo One or more commands failed.
    endlocal
    exit /b 1
)

echo All commands passed.
endlocal
exit /b 0

:run
set "LABEL=%~1"
set "COMMAND=%~2"
set "LOG=%TEMP%\check_%RANDOM%_%RANDOM%.log"

%COMMAND% >"%LOG%" 2>&1
set "RC=!ERRORLEVEL!"

if not "!RC!"=="0" (
    echo.
    echo ===== Error output: !LABEL! =====
    type "%LOG%"
    echo [FAIL] !LABEL!
    set "FAILED=1"
) else (
    findstr /L /C:"[관측]" "%LOG%"
    echo [PASS] !LABEL!
)

del "%LOG%" >nul 2>&1
exit /b 0