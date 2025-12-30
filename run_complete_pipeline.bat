@echo off
chcp 65001 >nul
echo ========================================
echo 完整流程：物体删除
echo ========================================
echo.

REM 设置默认参数
set VIDEO_PATH=inputs/object_removal/bmx-trees
set TEXT_PROMPT=car
set OUTPUT_DIR=results/pipeline

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :run
if "%~1"=="--video" (
    set VIDEO_PATH=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--text" (
    set TEXT_PROMPT=%~2
    set USE_TEXT=1
    shift
    shift
    goto :parse_args
)
if "%~1"=="--bbox" (
    set BBOX_INPUT=%~2
    set USE_BBOX=1
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--skip-inpaint" (
    set SKIP_INPAINT=--skip-inpaint
    shift
    goto :parse_args
)
shift
goto :parse_args

:run
echo 视频路径: %VIDEO_PATH%
if defined USE_TEXT (
    echo 文本提示: %TEXT_PROMPT%
    set INPUT_ARG=--text "%TEXT_PROMPT%"
) else if defined USE_BBOX (
    echo 边界框: %BBOX_INPUT%
    set INPUT_ARG=--bbox "%BBOX_INPUT%"
) else (
    echo 文本提示: %TEXT_PROMPT% (默认)
    set INPUT_ARG=--text "%TEXT_PROMPT%"
)
echo 输出目录: %OUTPUT_DIR%
echo.
echo 开始处理...
echo.

python complete_pipeline.py --video "%VIDEO_PATH%" %INPUT_ARG% --output "%OUTPUT_DIR%" %SKIP_INPAINT%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 处理成功完成！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 处理失败，请检查错误信息
    echo ========================================
)

pause








