# 🎬 ANALYZE VIDEO SKILL (BÓC TÁCH PHÂN CẢNH ĐIỆN ẢNH)

> **Kỹ năng phân tích video short-form chuyên sâu dành cho Antigravity AI Agent**  
> Hỗ trợ Instagram Reels, Instagram Carousel đa video, TikTok, Facebook Video và file MP4 cục bộ.

---

## ⚡ HƯỚNG DẪN CÀI ĐẶT 1 CHẠM

### 🌟 CÁCH 1: BẢO AI ANTIGRAVITY TỰ CÀI (KHUYÊN DÙNG)
Mở Antigravity lên và dán vào khung chat câu lệnh:

```text
Cài skill: https://github.com/vietndj/analyze-video
```

---

### 💻 CÁCH 2: DÁN 1 LỆNH VÀO TERMINAL

1. Trong Antigravity, bấm **`Control + \``** (Mac) hoặc **`Ctrl + \``** (Win) mở Terminal.
2. Dán lệnh cài đặt:

#### 👉 Cho macOS / Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/vietndj/analyze-video/main/install.sh | bash
```

#### 👉 Cho Windows (PowerShell):
```powershell
irm https://raw.githubusercontent.com/vietndj/analyze-video/main/install.ps1 | iex
```

3. Khởi động lại Antigravity.

---

## 🎯 CÁC TÍNH NĂNG NỔI BẬT

1. **Phát hiện cắt cảnh thông minh (OpenCV HSV Histogram)**: Tự động chia tách toàn bộ shot trong video.
2. **Trích xuất Keyframes 3 thì**: Start (Đầu) - Mid (Giữa) - End (Cuối) và ảnh chuyển cảnh Transition.
3. **Bóc tách chuẩn đạo diễn**:
   - **Tiêu đề phân cảnh**: Nêu rõ điểm hiệu quả nhất / logic thị giác đắt giá nhất + lý do vì sao.
   - **Mô tả đối tượng & diễn biến**: Bám sát bối cảnh thực tế.
   - **Đánh giá bố cục 2 chiều**: Phê bình khách quan cả mặt tốt lẫn mặt chưa tốt.
   - **Bài học thực chiến**: Đúc kết kinh nghiệm làm phim/video ngắn.
4. **Báo cáo Đạo Diễn HTML Mobile-First (< 80KB)**: Tích hợp Sticky Video Player, Drawer Jump Menu, Grid/Detail View.

---

## 🚀 CÚ PHÁP KÍCH HOẠT THỰC CHIẾN

Sau khi cài đặt xong, bạn chỉ cần gửi link hoặc file video vào chat:

* *"Phân tích video này giúp tôi: `https://www.instagram.com/reel/C8.../`"*
* *"Bóc tách phân cảnh video TikTok: `https://vt.tiktok.com/...`"*
* *"Phân tích video cục bộ: `/Users/.../video_mau.mp4`"*

---

© 2026 **FEDU Ecosystem** • Built for Antigravity AI Agents.
