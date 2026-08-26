# ==============================================================================
# ANALYZE VIDEO SKILL - ONE-CLICK INSTALLER (Windows PowerShell)
# ==============================================================================

$RepoUrl = "https://github.com/vietndj/analyze-video.git"
$TargetDir = "$env:USERPROFILE\.gemini\config\skills\analyze-video"
$TempDir = "$env:USERPROFILE\.gemini\.skill-analyze-video-temp"

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host " 🎬 CAI DAT KY NANG: ANALYZE VIDEO (BOC TACH PHAN CANH)" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Tao thu muc dich
if (!(Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

# 2. Tai ma nguon tu GitHub
if (Test-Path -Path "$TempDir\.git") {
    Write-Host "🔄 Dang dong bo phien ban moi nhat tu GitHub..." -ForegroundColor Blue
    Set-Location $TempDir
    git fetch --all --quiet
    git reset --hard origin/main --quiet
} else {
    Write-Host "📥 Dang tai ky nang analyze-video ve may..." -ForegroundColor Blue
    if (Test-Path -Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
    git clone --depth 1 $RepoUrl $TempDir --quiet
}

# 3. Dong bo vao thu muc Antigravity
Write-Host "📂 Dang thiet lap cau hinh ky nang vao Antigravity..." -ForegroundColor Blue
Copy-Item -Path "$TempDir\SKILL.md" -Destination "$TargetDir\SKILL.md" -Force
if (Test-Path -Path "$TempDir\scripts") {
    Copy-Item -Path "$TempDir\scripts" -Destination $TargetDir -Recurse -Force
}
if (Test-Path -Path "$TempDir\requirements.txt") {
    Copy-Item -Path "$TempDir\requirements.txt" -Destination $TargetDir -Force
}

# 4. Cai dat dependencies
Write-Host "📦 Dang kiem tra va cai dat thu vien (yt-dlp, opencv-python)..." -ForegroundColor Blue
pip install -q yt-dlp opencv-python numpy pillow requests

Write-Host ""
Write-Host "✅ CAI DAT THANH CONG KY NANG ANALYZE VIDEO!" -ForegroundColor Green
Write-Host "👉 Vi tri: $TargetDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "------------------------------------------------------" -ForegroundColor Cyan
Write-Host "💡 CACH SU DUNG TREN ANTIGRAVITY:" -ForegroundColor Green
Write-Host "1. Khoi dong lai hoac mo Antigravity."
Write-Host "2. Dan link video vao khung chat:"
Write-Host "   👉 'Phan tich video nay giup toi: https://www.instagram.com/reel/...'"
Write-Host "   👉 'Boc tach phan canh video nay: https://vt.tiktok.com/...'"
Write-Host "   👉 'Phan tich file video nay: C:\duong\dan\video.mp4'"
Write-Host "------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
