@echo off
setlocal
set "FAILED=0"

uv run --frozen python main.py run context
if errorlevel 1 (
    echo [FAIL] run context
    set "FAILED=1"
) else (
    echo [PASS] run context
)

uv run --frozen python main.py check context
if errorlevel 1 (
    echo [FAIL] check context
    set "FAILED=1"
) else (
    echo [PASS] check context
)

uv run --frozen python main.py run memory
if errorlevel 1 (
    echo [FAIL] run memory
    set "FAILED=1"
) else (
    echo [PASS] run memory
)

uv run --frozen python main.py check memory
if errorlevel 1 (
    echo [FAIL] check memory
    set "FAILED=1"
) else (
    echo [PASS] check memory
)

uv run --frozen python main.py run compare
if errorlevel 1 (
    echo [FAIL] run compare
    set "FAILED=1"
) else (
    echo [PASS] run compare
)

uv run --frozen python main.py check compare
if errorlevel 1 (
    echo [FAIL] check compare
    set "FAILED=1"
) else (
    echo [PASS] check compare
)

uv run --frozen python main.py run compare --live
if errorlevel 1 (
    echo [FAIL] run compare --live
    set "FAILED=1"
) else (
    echo [PASS] run compare --live
)

uv run --frozen python main.py run cache
if errorlevel 1 (
    echo [FAIL] run cache
    set "FAILED=1"
) else (
    echo [PASS] run cache
)

uv run --frozen python main.py check cache
if errorlevel 1 (
    echo [FAIL] check cache
    set "FAILED=1"
) else (
    echo [PASS] check cache
)

uv run --frozen python main.py run cache --live
if errorlevel 1 (
    echo [FAIL] run cache --live
    set "FAILED=1"
) else (
    echo [PASS] run cache --live
)

if "%FAILED%"=="1" (
    echo One or more commands failed.
    endlocal
    exit /b 1
)

echo All commands passed.
endlocal
exit /b 0
