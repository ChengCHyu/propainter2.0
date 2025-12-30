@echo off
chcp 65001 >nul
echo ========================================
echo 成员A：文本到边界框转换
echo ========================================
echo.

REM 设置默认参数
set VIDEO_PATH=inputs/object_removal/bmx-trees
set TEXT_PROMPT=car
set OUTPUT_PATH=results/member_a_bboxes/bboxes.json

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
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set OUTPUT_PATH=%~2
    shift
    shift
    goto :parse_args
)
shift
goto :parse_args

:run
echo 视频路径: %VIDEO_PATH%
echo 文本提示: %TEXT_PROMPT%
echo 输出路径: %OUTPUT_PATH%
echo.
echo 开始处理...
echo.

python member_a/text_to_bbox.py --video "%VIDEO_PATH%" --text "%TEXT_PROMPT%" --output "%OUTPUT_PATH%"

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








