# 成员B：分割与追踪模块
# 使用方法：
#   .\run_member_b.ps1
#   .\run_member_b.ps1 -VideoPath "inputs/object_removal/bmx-trees" -BboxFile "results/member_a_bboxes/bboxes.json"
#   .\run_member_b.ps1 -VideoPath "inputs/object_removal/bmx-trees" -BboxString "[[180, 60, 285, 181]]"

param(
    [string]$VideoPath = "inputs/object_removal/bmx-trees",
    [string]$BboxFile = "results/member_a_bboxes/bboxes.json",
    [string]$BboxString = "",
    [string]$OutputPath = "results/member_b_masks/bmx-trees"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "成员B：分割与追踪模块" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "视频路径: $VideoPath"
if ($BboxString -ne "") {
    Write-Host "边界框字符串: $BboxString"
    $bboxArg = $BboxString
} else {
    Write-Host "边界框文件: $BboxFile"
    $bboxArg = $BboxFile
}
Write-Host "输出路径: $OutputPath"
Write-Host ""
Write-Host "开始处理..." -ForegroundColor Yellow
Write-Host ""

$scriptPath = "member_b/member_b_track_anything.py"
$arguments = @(
    "--video", $VideoPath,
    "--bbox", $bboxArg,
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
