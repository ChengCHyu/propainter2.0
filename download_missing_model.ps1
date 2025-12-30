# Download missing recurrent_flow_completion.pth model

Write-Host "Downloading recurrent_flow_completion.pth..." -ForegroundColor Cyan
Write-Host ""

$targetDir = "D:\XUEXI\ProPainter\weights"
$fileName = "recurrent_flow_completion.pth"
$targetPath = Join-Path $targetDir $fileName
$url = "https://github.com/sczhou/ProPainter/releases/download/v0.1.0/recurrent_flow_completion.pth"

# Check if file already exists
if (Test-Path $targetPath) {
    $size = (Get-Item $targetPath).Length / 1MB
    Write-Host "File already exists: $targetPath" -ForegroundColor Green
    Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Green
    exit 0
}

# Ensure directory exists
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Write-Host "Created directory: $targetDir" -ForegroundColor Yellow
}

Write-Host "Target directory: $targetDir" -ForegroundColor White
Write-Host "Target file: $fileName" -ForegroundColor White
Write-Host "Download URL: $url" -ForegroundColor White
Write-Host ""

try {
    Write-Host "Downloading..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $url -OutFile $targetPath -ErrorAction Stop
    
    if (Test-Path $targetPath) {
        $size = (Get-Item $targetPath).Length / 1MB
        Write-Host ""
        Write-Host "Download completed successfully!" -ForegroundColor Green
        Write-Host "File saved to: $targetPath" -ForegroundColor Green
        Write-Host "File size: $([math]::Round($size, 2)) MB" -ForegroundColor Green
    } else {
        Write-Host "Download failed: File not found after download" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "Download failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download manually:" -ForegroundColor Yellow
    Write-Host "  URL: $url" -ForegroundColor Yellow
    Write-Host "  Save to: $targetPath" -ForegroundColor Yellow
    exit 1
}








