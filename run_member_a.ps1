# 成员A：文本到边界框转换
# 使用方法：
#   .\run_member_a.ps1
#   .\run_member_a.ps1 -VideoPath "inputs/object_removal/bmx-trees" -TextPrompt "car"
#   .\run_member_a.ps1 -VideoPath "inputs/object_removal/bmx-trees" -TextPrompt "car" -OutputPath "results/member_a_bboxes/bboxes.json"

param(
    [string]$VideoPath = "inputs/object_removal/bmx-trees",
    [string]$TextPrompt = "car",
    [string]$OutputPath = "results/member_a_bboxes/bboxes.json"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "成员A：文本到边界框转换" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "视频路径: $VideoPath"
Write-Host "文本提示: $TextPrompt"
Write-Host "输出路径: $OutputPath"
Write-Host ""
Write-Host "开始处理..." -ForegroundColor Yellow
Write-Host ""

$scriptPath = "member_a/text_to_bbox.py"
$arguments = @(
    "--video", $VideoPath,
    "--text", $TextPrompt,
    "--output", $OutputPath
)

python $scriptPath $arguments

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "处理成功完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "处理失败，请检查错误信息" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}








