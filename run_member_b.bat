@echo off
chcp 65001 >nul
echo ========================================
echo 成员B：分割与追踪模块
echo ========================================
echo.

REM 设置默认参数
set VIDEO_PATH=inputs/object_removal/bmx-trees
set BBOX_FILE=results/member_a_bboxes/bboxes.json
set OUTPUT_PATH=results/member_b_masks/bmx-trees

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :run
if "%~1"=="--video" (
    set VIDEO_PATH=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--bbox" (
    set BBOX_FILE=%~2
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
echo 边界框: %BBOX_FILE%
echo 输出路径: %OUTPUT_PATH%
echo.
echo 开始处理...
echo.

python member_b/member_b_track_anything.py --video "%VIDEO_PATH%" --bbox "%BBOX_FILE%" --output "%OUTPUT_PATH%"

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
