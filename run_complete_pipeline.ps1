# 完整流程：物体删除
# 使用方法：
#   .\run_complete_pipeline.ps1
#   .\run_complete_pipeline.ps1 -VideoPath "inputs/object_removal/bmx-trees" -TextPrompt "car"
#   .\run_complete_pipeline.ps1 -VideoPath "inputs/object_removal/bmx-trees" -BboxString "[[180, 60, 285, 181]]"
#   .\run_complete_pipeline.ps1 -VideoPath "inputs/object_removal/bmx-trees" -TextPrompt "car" -SkipInpaint

param(
    [string]$VideoPath = "inputs/object_removal/bmx-trees",
    [string]$TextPrompt = "",
    [string]$BboxString = "",
    [string]$BboxFile = "",
    [string]$OutputDir = "results/pipeline",
    [switch]$SkipInpaint = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完整流程：物体删除" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "视频路径: $VideoPath"

$arguments = @()
$arguments += "--video"
$arguments += $VideoPath

if ($BboxFile -ne "") {
    Write-Host "边界框文件: $BboxFile"
    $arguments += "--bbox"
    $arguments += $BboxFile
}
elseif ($BboxString -ne "") {
    Write-Host "边界框: $BboxString"
    $arguments += "--bbox"
    $arguments += $BboxString
}
elseif ($TextPrompt -ne "") {
    Write-Host "文本提示: $TextPrompt"
    $arguments += "--text"
    $arguments += $TextPrompt
}
else {
    Write-Host "错误: 必须提供 --text 或 --bbox 参数" -ForegroundColor Red
    exit 1
}

Write-Host "输出目录: $OutputDir"
$arguments += "--output"
$arguments += $OutputDir

if ($SkipInpaint) {
    Write-Host "跳过ProPainter修复" -ForegroundColor Yellow
    $arguments += "--skip-inpaint"
}

Write-Host ""
Write-Host "开始处理..." -ForegroundColor Yellow
Write-Host ""

python complete_pipeline.py $arguments

$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "处理成功完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "处理失败，请检查错误信息" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}
