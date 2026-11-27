@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "RESULTS="
set "FAILED=0"

call :run "run context" "uv run --frozen python main.py run context"
call :run "check context" "uv run --frozen python main.py check context"
call :run "run memory" "uv run --frozen python main.py run memory"
call :run "check memory" "uv run --frozen python main.py check memory"
call :run "run compare" "uv run --frozen python main.py run compare"
call :run "check compare" "uv run --frozen python main.py check compare"
call :run "run compare --live" "uv run --frozen python main.py run compare --live"
call :run "run cache" "uv run --frozen python main.py run cache"
call :run "check cache" "uv run --frozen python main.py check cache"
call :run "run cache --live" "uv run --frozen python main.py run cache --live"

echo.
echo ===== Results =====
echo !RESULTS!
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
echo Running !LABEL!...
%COMMAND% >nul 2>&1
if errorlevel 1 (
    set "RESULTS=!RESULTS![FAIL] !LABEL!; "
    set "FAILED=1"
) else (
    set "RESULTS=!RESULTS![PASS] !LABEL!; "
)
exit /b 0
