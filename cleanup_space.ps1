# 清理项目空间
# 删除可以重新生成的文件和缓存

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "项目空间清理工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 询问用户要清理什么
Write-Host "请选择要清理的内容:" -ForegroundColor Yellow
Write-Host "1. 输出文件 (outputs目录，包括处理后的视频和掩码)" -ForegroundColor White
Write-Host "2. 上传文件 (uploads目录，包括用户上传的视频)" -ForegroundColor White
Write-Host "3. 结果文件 (results目录，包括旧的测试结果)" -ForegroundColor White
Write-Host "4. Python缓存 (__pycache__目录)" -ForegroundColor White
Write-Host "5. 全部清理 (1+2+3+4)" -ForegroundColor White
Write-Host "0. 取消" -ForegroundColor White
Write-Host ""

$choice = Read-Host "请输入选项 (0-5)"

$cleaned = @()

switch ($choice) {
    "1" {
        $path = "video_object_removal_web\outputs"
        if (Test-Path $path) {
            $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "正在删除 $path ..." -ForegroundColor Yellow
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "已删除，释放空间: $sizeMB MB" -ForegroundColor Green
            $cleaned += "outputs"
        }
    }
    "2" {
        $path = "video_object_removal_web\uploads"
        if (Test-Path $path) {
            $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "正在删除 $path ..." -ForegroundColor Yellow
            Get-ChildItem -Path $path -File | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Host "已删除，释放空间: $sizeMB MB" -ForegroundColor Green
            $cleaned += "uploads"
        }
    }
    "3" {
        $path = "results"
        if (Test-Path $path) {
            $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "正在删除 $path ..." -ForegroundColor Yellow
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "已删除，释放空间: $sizeMB MB" -ForegroundColor Green
            $cleaned += "results"
        }
    }
    "4" {
        Write-Host "正在删除所有 __pycache__ 目录..." -ForegroundColor Yellow
        $totalSize = 0
        Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
            $size = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $totalSize += $size
            Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
        $sizeMB = [math]::Round($totalSize / 1MB, 2)
        Write-Host "已删除，释放空间: $sizeMB MB" -ForegroundColor Green
        $cleaned += "__pycache__"
    }
    "5" {
        Write-Host "正在清理全部..." -ForegroundColor Yellow
        
        # 清理outputs
        $path = "video_object_removal_web\outputs"
        if (Test-Path $path) {
            $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            $cleaned += "outputs"
        }
        
        # 清理uploads
        $path = "video_object_removal_web\uploads"
        if (Test-Path $path) {
            $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            Get-ChildItem -Path $path -File | Remove-Item -Force -ErrorAction SilentlyContinue
            $cleaned += "uploads"
        }
        
        # 清理results
        $path = "results"
        if (Test-Path $path) {
            $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
            $cleaned += "results"
        }
        
        # 清理__pycache__
        Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
        $cleaned += "__pycache__"
        
        Write-Host "全部清理完成！" -ForegroundColor Green
    }
    "0" {
        Write-Host "已取消" -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "无效选项" -ForegroundColor Red
        exit
    }
}

if ($cleaned.Count -gt 0) {
    Write-Host ""
    Write-Host "清理完成！已清理: $($cleaned -join ', ')" -ForegroundColor Green
} else {
    Write-Host "没有清理任何内容" -ForegroundColor Yellow
}







