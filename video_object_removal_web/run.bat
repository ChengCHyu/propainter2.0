@echo off
chcp 65001 >nul
echo ========================================
echo 启动视频物体删除 Web 应用
echo ========================================
echo.

cd /d %~dp0

echo 检查依赖...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
    echo.
)

echo 启动服务器...
echo 访问 http://127.0.0.1:5000 使用前端界面
echo.
python app.py

pause








