#!/bin/bash
# ==============================================================================
# ANALYZE VIDEO SKILL - ONE-CLICK INSTALLER (macOS / Linux)
# ==============================================================================

set -e

REPO_URL="https://github.com/vietndj/analyze-video.git"
TARGET_DIR="$HOME/.gemini/config/skills/analyze-video"
TEMP_DIR="$HOME/.gemini/.skill-analyze-video-temp"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}======================================================${NC}"
echo -e "${GREEN} 🎬 CÀI ĐẶT KỸ NĂNG: ANALYZE VIDEO (BÓC TÁCH PHÂN CẢNH)${NC}"
echo -e "${CYAN}======================================================${NC}"
echo ""

# 1. Tạo thư mục đích
mkdir -p "$TARGET_DIR"

# 2. Tải mã nguồn từ GitHub
if [ -d "$TEMP_DIR/.git" ]; then
    echo -e "${BLUE}🔄 Đang đồng bộ phiên bản mới nhất từ GitHub...${NC}"
    cd "$TEMP_DIR"
    git fetch --all --quiet
    git reset --hard origin/main --quiet || git pull --quiet
else
    echo -e "${BLUE}📥 Đang tải kỹ năng analyze-video về máy...${NC}"
    rm -rf "$TEMP_DIR"
    git clone --depth 1 "$REPO_URL" "$TEMP_DIR" --quiet
fi

# 3. Đồng bộ vào thư mục Antigravity
echo -e "${BLUE}📂 Đang thiết lập cấu hình kỹ năng vào Antigravity...${NC}"
cp -rf "$TEMP_DIR"/SKILL.md "$TARGET_DIR"/
cp -rf "$TEMP_DIR"/scripts "$TARGET_DIR"/ 2>/dev/null || true
cp -rf "$TEMP_DIR"/requirements.txt "$TARGET_DIR"/ 2>/dev/null || true

# 4. Tự động cài đặt thư viện phụ trợ (yt-dlp, opencv-python, numpy)
echo -e "${BLUE}📦 Đang kiểm tra và cài đặt thư viện cần thiết (yt-dlp, opencv-python)...${NC}"
pip3 install -q yt-dlp opencv-python numpy pillow requests || true

echo ""
echo -e "${GREEN}✅ CÀI ĐẶT THÀNH CÔNG KỸ NĂNG ANALYZE VIDEO!${NC}"
echo -e "${YELLOW}👉 Vị trí: ${TARGET_DIR}${NC}"
echo ""
echo -e "${CYAN}------------------------------------------------------${NC}"
echo -e "${GREEN}💡 CÁCH SỬ DỤNG TRÊN ANTIGRAVITY:${NC}"
echo "1. Khởi động lại hoặc mở Antigravity."
echo "2. Dán link video vào khung chat:"
echo "   👉 'Phân tích video này giúp tôi: https://www.instagram.com/reel/...'"
echo "   👉 'Bóc tách phân cảnh video này: https://vt.tiktok.com/...'"
echo "   👉 'Phân tích file video này: /duong/dan/video.mp4'"
echo -e "${CYAN}------------------------------------------------------${NC}"
echo ""
