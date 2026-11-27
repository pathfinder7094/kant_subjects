@echo off
setlocal
for /f "tokens=2 delims=:" %%A in ('chcp') do set "ORIGINAL_CODEPAGE=%%A"
set "ORIGINAL_CODEPAGE=%ORIGINAL_CODEPAGE: =%"
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"

if not exist "artifacts" mkdir "artifacts"
if errorlevel 1 (
    echo [FAIL] create artifacts directory
    if defined ORIGINAL_CODEPAGE chcp %ORIGINAL_CODEPAGE% >nul
    endlocal
    exit /b 1
)

set "LOG=%~dp0artifacts\check-output.log"
> "%LOG%" echo Captured output from check.cmd

echo Running commands; detailed output will appear at the end.
echo [1/10] run context
call :run 01 "run context" uv run --frozen python main.py run context
echo [2/10] check context
call :run 02 "check context" uv run --frozen python main.py check context
echo [3/10] run memory
call :run 03 "run memory" uv run --frozen python main.py run memory
echo [4/10] check memory
call :run 04 "check memory" uv run --frozen python main.py check memory
echo [5/10] run compare
call :run 05 "run compare" uv run --frozen python main.py run compare
echo [6/10] check compare
call :run 06 "check compare" uv run --frozen python main.py check compare
echo [7/10] run compare --live
call :run 07 "run compare --live" uv run --frozen python main.py run compare --live
echo [8/10] run cache
call :run 08 "run cache" uv run --frozen python main.py run cache
echo [9/10] check cache
call :run 09 "check cache" uv run --frozen python main.py check cache
echo [10/10] run cache --live
call :run 10 "run cache --live" uv run --frozen python main.py run cache --live

set "OBSERVATION_FAILED=0"
set "OBSERVATIONS=0"
if "%RESULT_05%"=="0" call :observe-compare fixture artifacts\compare-fixture.json
if "%RESULT_07%"=="0" call :observe-compare live artifacts\compare-live.json
if "%RESULT_08%"=="0" call :observe-cache fixture artifacts\cache-fixture.json
if "%RESULT_10%"=="0" call :observe-cache live artifacts\cache-live.json

echo.
echo ===== Final results =====
set "FAILED=0"
if "%RESULT_01%"=="0" (echo [PASS] run context) else (echo [FAIL] run context)
if not "%RESULT_01%"=="0" set "FAILED=1"
if "%RESULT_02%"=="0" (echo [PASS] check context) else (echo [FAIL] check context)
if not "%RESULT_02%"=="0" set "FAILED=1"
if "%RESULT_03%"=="0" (echo [PASS] run memory) else (echo [FAIL] run memory)
if not "%RESULT_03%"=="0" set "FAILED=1"
if "%RESULT_04%"=="0" (echo [PASS] check memory) else (echo [FAIL] check memory)
if not "%RESULT_04%"=="0" set "FAILED=1"
if "%RESULT_05%"=="0" (echo [PASS] run compare) else (echo [FAIL] run compare)
if not "%RESULT_05%"=="0" set "FAILED=1"
if "%RESULT_06%"=="0" (echo [PASS] check compare) else (echo [FAIL] check compare)
if not "%RESULT_06%"=="0" set "FAILED=1"
if "%RESULT_07%"=="0" (echo [PASS] run compare --live) else (echo [FAIL] run compare --live)
if not "%RESULT_07%"=="0" set "FAILED=1"
if "%RESULT_08%"=="0" (echo [PASS] run cache) else (echo [FAIL] run cache)
if not "%RESULT_08%"=="0" set "FAILED=1"
if "%RESULT_09%"=="0" (echo [PASS] check cache) else (echo [FAIL] check cache)
if not "%RESULT_09%"=="0" set "FAILED=1"
if "%RESULT_10%"=="0" (echo [PASS] run cache --live) else (echo [FAIL] run cache --live)
if not "%RESULT_10%"=="0" set "FAILED=1"

if "%OBSERVATION_FAILED%"=="1" (
    echo [FAIL] observation report
    set "FAILED=1"
) else if "%OBSERVATIONS%"=="1" (
    echo [PASS] observation report
)

if "%FAILED%"=="1" (
    >>"%LOG%" echo.
    >>"%LOG%" echo Overall result: FAIL
    echo.
    echo ===== Detailed command output =====
    type "%LOG%"
    echo.
    echo Overall result: FAIL
    echo One or more commands failed.
    if defined ORIGINAL_CODEPAGE chcp %ORIGINAL_CODEPAGE% >nul
    endlocal
    exit /b 1
)

>>"%LOG%" echo.
>>"%LOG%" echo Overall result: PASS
echo.
echo ===== Detailed command output =====
type "%LOG%"
echo.
echo Overall result: PASS
echo All commands passed.
if defined ORIGINAL_CODEPAGE chcp %ORIGINAL_CODEPAGE% >nul
endlocal
exit /b 0

:run
set "ID=%~1"
set "LABEL=%~2"
shift
shift
>>"%LOG%" echo.
>>"%LOG%" echo ===== %LABEL% =====
%1 %2 %3 %4 %5 %6 %7 %8 %9 >>"%LOG%" 2>&1
set "RESULT_%ID%=%ERRORLEVEL%"
exit /b 0

:observe-compare
set "OBSERVATIONS=1"
>>"%LOG%" echo.
>>"%LOG%" echo ===== Observation: compare %~1 =====
uv run --frozen python -c "import json,pathlib,sys; expected=json.loads(pathlib.Path(r'data\scenario.json').read_text(encoding='utf-8'))['expected']; report=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')); [print('{}: limit={} budget={} tokens={} turns={} missing={}'.format(row['condition'],row['limit'],row['input_budget'],row['estimated_input_tokens'],','.join(row['turn_ids']) or 'none',','.join(name for name,value in expected.items() if row['answer'].get(name)!=value) or 'none')) for row in report['records']]" "%~2" >>"%LOG%" 2>&1
if errorlevel 1 (
    >>"%LOG%" echo [FAIL] Could not generate compare observation.
    set "OBSERVATION_FAILED=1"
)
exit /b 0

:observe-cache
set "OBSERVATIONS=1"
>>"%LOG%" echo.
>>"%LOG%" echo ===== Observation: cache %~1 =====
uv run --frozen python -c "import json,pathlib,sys; report=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')); rows=report['records']; print('실제 사용량과 비용 미관측 (fixture mode)' if not rows else '실제 캐시 사용량 및 비용:'); [print('cache_enabled={} input={} cached={} write={} output={} cost_usd={} observation={}'.format(row['cache_enabled'],(row.get('usage') or {}).get('input_tokens','n/a'),((row.get('usage') or {}).get('input_tokens_details') or {}).get('cached_tokens','n/a'),((row.get('usage') or {}).get('input_tokens_details') or {}).get('cache_write_tokens','n/a'),(row.get('usage') or {}).get('output_tokens','n/a'),row.get('estimated_cost_usd','n/a'),row.get('cache_observation','미관측'))) for row in rows]" "%~2" >>"%LOG%" 2>&1
if errorlevel 1 (
    >>"%LOG%" echo [FAIL] Could not generate cache observation.
    set "OBSERVATION_FAILED=1"
)
exit /b 0
