# Download and setup John the Ripper for Windows
$johnUrl = "https://www.openwall.com/john/k/john-1.9.0-jumbo-1-win64.zip"
$zipFile = "john.zip"
$extractPath = "john"

Write-Host "Downloading John the Ripper..." -ForegroundColor Green
Invoke-WebRequest -Uri $johnUrl -OutFile $zipFile

Write-Host "Extracting..." -ForegroundColor Green
Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

Write-Host "John the Ripper installed!" -ForegroundColor Green
Write-Host "Location: $extractPath" -ForegroundColor Yellow

# Find pdf2john
$pdf2john = Get-ChildItem -Path $extractPath -Recurse -Filter "pdf2john.pl" | Select-Object -First 1

if ($pdf2john) {
    Write-Host "Found pdf2john at: $($pdf2john.FullName)" -ForegroundColor Green
} else {
    Write-Host "pdf2john not found, trying Python version..." -ForegroundColor Yellow
}
