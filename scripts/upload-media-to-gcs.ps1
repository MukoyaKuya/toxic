# Upload local media files to Google Cloud Storage for production
# Run from project root: .\scripts\upload-media-to-gcs.ps1 -Bucket "your-bucket-name"

param(
    [Parameter(Mandatory=$true)]
    [string]$Bucket,
    
    [switch]$Public
)

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$mediaPath = Join-Path $projectRoot "media"
if (-not (Test-Path $mediaPath)) {
    Write-Error "media/ folder not found at $mediaPath"
    exit 1
}

Write-Host "Uploading media from $mediaPath to gs://$Bucket/ ..."
$opts = @("-m", "cp", "-r")
if ($Public) { $opts += "-a", "public-read" }
$opts += (Join-Path $mediaPath "*")
$opts += "gs://$Bucket/"

& gsutil @opts

Write-Host "Done. To make bucket publicly readable: gsutil iam ch allUsers:objectViewer gs://$Bucket"
