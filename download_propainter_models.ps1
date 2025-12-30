# Download ProPainter model files to weights directory

Write-Host "Downloading ProPainter model files..." 
Write-Host ""

# Ensure weights directory exists
if (-not (Test-Path "weights")) {
    New-Item -ItemType Directory -Path "weights" | Out-Null
    Write-Host "Created weights directory" 
}

$baseUrl = "https://github.com/sczhou/ProPainter/releases/download/v0.1.0/"
$models = @(
    @{Name="recurrent_flow_completion.pth"; Size="~30 MB"},
    @{Name="ProPainter.pth"; Size="~170 MB"}
)

foreach ($model in $models) {
    $modelPath = Join-Path "weights" $model.Name
    
    if (Test-Path $modelPath) {
        $fileSize = (Get-Item $modelPath).Length / 1MB
        Write-Host "[OK] Exists: $($model.Name) ($([math]::Round($fileSize, 2)) MB)" 
    } else {
        Write-Host "Downloading: $($model.Name) ($($model.Size))..." 
        $url = $baseUrl + $model.Name
        
        try {
            Invoke-WebRequest -Uri $url -OutFile $modelPath -ErrorAction Stop
            $fileSize = (Get-Item $modelPath).Length / 1MB
            Write-Host "[OK] Downloaded: $($model.Name) ($([math]::Round($fileSize, 2)) MB)" 
        } catch {
            Write-Host "[ERROR] Failed to download: $($model.Name)" 
            Write-Host "  Error: $($_.Exception.Message)" 
            Write-Host "  Please download manually: $url" 
        }
    }
    Write-Host ""
}

Write-Host "Done!"

