# Check disk space usage
# Find files and directories consuming disk space

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Disk Space Usage Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check directories
$dirs = @(
    @{Name="weights (model files)"; Path="weights"},
    @{Name="video_object_removal_web\outputs (output videos)"; Path="video_object_removal_web\outputs"},
    @{Name="video_object_removal_web\uploads (uploaded videos)"; Path="video_object_removal_web\uploads"},
    @{Name="results (result directory)"; Path="results"},
    @{Name="inputs (input directory)"; Path="inputs"},
    @{Name="__pycache__ (Python cache)"; Path="__pycache__"}
)

$totalSize = 0

foreach ($dir in $dirs) {
    if (Test-Path $dir.Path) {
        $files = Get-ChildItem -Path $dir.Path -Recurse -File -ErrorAction SilentlyContinue
        if ($files) {
            $size = ($files | Measure-Object -Property Length -Sum).Sum
            $sizeGB = [math]::Round($size / 1GB, 2)
            $sizeMB = [math]::Round($size / 1MB, 2)
            $fileCount = $files.Count
            $totalSize += $size
            
            if ($sizeGB -gt 0.1) {
                Write-Host "$($dir.Name):" -ForegroundColor Yellow
                Write-Host "  Size: $sizeGB GB ($sizeMB MB)" -ForegroundColor White
                Write-Host "  Files: $fileCount" -ForegroundColor White
            } else {
                Write-Host "$($dir.Name): $sizeMB MB ($fileCount files)" -ForegroundColor Gray
            }
        } else {
            Write-Host "$($dir.Name): empty directory" -ForegroundColor Gray
        }
    } else {
        Write-Host "$($dir.Name): not found" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
$totalGB = [math]::Round($totalSize / 1GB, 2)
$totalMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "Total Size: $totalGB GB ($totalMB MB)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check largest files
Write-Host "Top 10 largest files:" -ForegroundColor Cyan
Get-ChildItem -Path "." -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notlike "*\.venv\*" -and $_.FullName -notlike "*\node_modules\*" } |
    Sort-Object Length -Descending | 
    Select-Object -First 10 | 
    ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 2)
        $relativePath = $_.FullName.Replace((Get-Location).Path + "\", "")
        Write-Host "  $sizeMB MB - $relativePath" -ForegroundColor White
    }

Write-Host ""
Write-Host "Tips: You can delete the following to free space:" -ForegroundColor Green
Write-Host "  1. video_object_removal_web\outputs\* (processed videos and masks, can be regenerated)" -ForegroundColor Green
Write-Host "  2. video_object_removal_web\uploads\* (uploaded videos, can be re-uploaded)" -ForegroundColor Green
Write-Host "  3. results\* (old test results)" -ForegroundColor Green
Write-Host "  4. __pycache__\ (Python cache, will be regenerated automatically)" -ForegroundColor Green
Write-Host "  5. .venv\ (virtual environment, can be reinstalled)" -ForegroundColor Green
