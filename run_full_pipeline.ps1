# 完整流程：成员A + 成员B
# 使用方法：
#   .\run_full_pipeline.ps1
#   .\run_full_pipeline.ps1 -VideoPath "inputs/object_removal/bmx-trees" -TextPrompt "car"

param(
    [string]$VideoPath = "inputs/object_removal/bmx-trees",
    [string]$TextPrompt = "car"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完整流程：成员A + 成员B" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "视频路径: $VideoPath"
Write-Host "文本提示: $TextPrompt"
Write-Host ""

# 步骤1：成员A
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "步骤1：运行成员A（文本到边界框）" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$bboxOutput = "results/member_a_bboxes/temp_bboxes.json"

$scriptPathA = "member_a/text_to_bbox.py"
$argumentsA = @(
    "--video", $VideoPath,
    "--text", $TextPrompt,
    "--output", $bboxOutput
)

python $scriptPathA $argumentsA

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "成员A处理失败，终止流程" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "成员A处理完成！" -ForegroundColor Green
Write-Host ""

# 步骤2：成员B
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "步骤2：运行成员B（分割与追踪）" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# 从视频路径提取名称作为输出文件夹名
$videoName = [System.IO.Path]::GetFileNameWithoutExtension($VideoPath)
$maskOutput = "results/member_b_masks/$videoName"

$scriptPathB = "member_b/member_b_track_anything.py"
$argumentsB = @(
    "--video", $VideoPath,
    "--bbox", $bboxOutput,
    "--output", $maskOutput
)

python $scriptPathB $argumentsB

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "成员B处理失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "完整流程处理成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "输出掩码路径: $maskOutput" -ForegroundColor Cyan
Write-Host ""








