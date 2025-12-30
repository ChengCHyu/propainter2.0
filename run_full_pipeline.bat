@echo off
chcp 65001 >nul
echo ========================================
echo 完整流程：成员A + 成员B
echo ========================================
echo.

REM 设置默认参数
set VIDEO_PATH=inputs/object_removal/bmx-trees
set TEXT_PROMPT=car

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
shift
goto :parse_args

:run
echo 视频路径: %VIDEO_PATH%
echo 文本提示: %TEXT_PROMPT%
echo.

REM 步骤1：成员A
echo ========================================
echo 步骤1：运行成员A（文本到边界框）
echo ========================================
echo.

set BBOX_OUTPUT=results/member_a_bboxes/temp_bboxes.json
python member_a/text_to_bbox.py --video "%VIDEO_PATH%" --text "%TEXT_PROMPT%" --output "%BBOX_OUTPUT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 成员A处理失败，终止流程
    pause
    exit /b 1
)

echo.
echo 成员A处理完成！
echo.

REM 步骤2：成员B
echo ========================================
echo 步骤2：运行成员B（分割与追踪）
echo ========================================
echo.

REM 从视频路径提取名称作为输出文件夹名
for %%F in ("%VIDEO_PATH%") do set VIDEO_NAME=%%~nF
set MASK_OUTPUT=results/member_b_masks/%VIDEO_NAME%

python member_b/member_b_track_anything.py --video "%VIDEO_PATH%" --bbox "%BBOX_OUTPUT%" --output "%MASK_OUTPUT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 成员B处理失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 完整流程处理成功！
echo ========================================
echo.
echo 输出掩码路径: %MASK_OUTPUT%
echo.

pause








