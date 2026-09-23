---
name: analyze-video
description: "Kích hoạt khi người dùng gửi link video (Instagram Reels, TikTok, YouTube Shorts, FB Video) hoặc yêu cầu phân tích video, bóc tách phân cảnh, mổ xẻ kịch bản video thực chiến."
---

# KỸ NĂNG PHÂN TÍCH & BÓC TÁCH VIDEO THỰC CHIẾN (ANALYZE VIDEO SKILL)

## 📌 NGUYÊN TẮC VÀNG VỀ TRẬT TỰ THỰC THI (CHAT-FIRST LAW)

1. **ƯU TIÊN SỐ 1 — TRẢ KẾT QUẢ VÀO CHAT NGAY LẬP TỨC (ZERO LATENCY)**:
   - Khi có link video, AI bóc tách nội dung và **XUẤT BẢN NGAY BÁO CÁO PHÂN TÍCH VÀO CHAT** theo chuẩn **Gạch Đầu Dòng Tối Giản (5 ý/shot)**.
   - **TUYỆT ĐỐI KHÔNG CHỜ** deploy web, không chờ upload R2/Drive mới trả lời. Người dùng cần đọc phân tích ngay lập tức.
   - **TUYỆT ĐỐI KHÔNG BÁO CÁO KỸ THUẬT RÁC**: Không giải thích dài dòng về bug code, server restart, token hay log pipeline trừ khi người dùng hỏi.

2. **TIẾN TRÌNH HẠ TẦNG CHẠY NGẦM HOÀN TOÀN (BACKGROUND SYNC)**:
   - Việc tải video gốc, render webp, upload Cloudflare R2, Google Drive, cập nhật `scene.html` và deploy `ytuong.fedu.vn` phải chạy ngầm bằng script.
   - Nếu tiến trình hạ tầng gặp sự cố, TUYỆT ĐỐI KHÔNG làm gián đoạn hay trì hoãn việc xuất bản nội dung mổ băng cho người dùng trong chat.

---

## 📌 QUY TẮC ĐỊNH TUYẾN LINK TỰ ĐỘNG (SMART URL ROUTING)
- **Áp dụng cho**: Link **Instagram** (`reel`, `/p/`, `tv`), **TikTok**, **Facebook Video/Reels**, hoặc file video `.mp4` cục bộ.
- **LOẠI TRỪ YOUTUBE DÀI**: Link podcast dài trên YouTube chuyển sang kỹ năng **`phan-tich-podcast-youtube`**. Shorts YouTube vẫn xử lý được.

---

## BƯỚC 1: KIỂM TRA TRÙNG LẶP TRONG SCENE.HTML (PRE-CHECK DUPLICATION)
Trước khi tải hay bóc tách, kiểm tra xem video này đã có trong `scene.html` chưa:
```bash
python3 "/Users/vietmac/Documents/CODE/Quản gia/check_scene_duplicate.py" "<LINK_HOẶC_SHORTCODE>"
```
- **NẾU ĐÃ CÓ (`exists: true`)**:
  - Dừng ngay việc tải lại hay tạo thư mục mới.
  - Báo ngay cho người dùng kèm các link:
    - 📱 **Xem Báo Cáo:** `https://ytuong.fedu.vn/reports/[folder_name].html`
    - 🌐 **Kho Ý Tưởng:** `https://ytuong.fedu.vn`
    - 📁 **Google Drive:** `[Link Drive]` (nếu có)
  - Xuất tóm tắt 3 dòng về nội dung cốt lõi và kết thúc.
- **NẾU CHƯA CÓ (`exists: false`)**:
  - Tiếp tục sang Bước 2 và Bước 3.

---

## BƯỚC 2: BÓC TÁCH TƯ LIỆU BẰNG SCRIPT
Chạy script phân tích và trích xuất khung hình:
```bash
python3 "/Users/vietmac/Documents/CODE/analyze-video/analyze_and_upload.py" "<LINK>"
```
*(Hoặc script storyboard: `python3 "/Users/vietmac/Documents/CODE/AI Course/.agents/skills/analyze-video/scripts/extract_storyboard.py" "<LINK>"`)*

---

## BƯỚC 3: QUY CHUẨN TRÌNH BÀY BÁO CÁO TRONG CHAT (CHUẨN GẠCH ĐẦU DÒNG TỐI GIẢN)

Mỗi báo cáo phân tích BẮT BUỘC giữ ĐẦY ĐỦ giá trị thực chiến nhưng **TUYỆT ĐỐI KHÔNG VIẾT VĂN XUÔI DÀI DÒNG, KHÔNG DÙNG VĂN MẪU/TEMPLATE ẢO**. Toàn bộ báo cáo phải tuân thủ đúng cấu trúc 4 phần sau:

### 1. TIÊU ĐỀ & LIÊN KẾT ĐIỀU HƯỚNG (SMART LINKS)
```markdown
# [Tên Đòn Bẩy Thị Giác / Kỹ Thuật Đắt Giá Nhất Của Video]
**Nguồn:** [@Tên_Creator](Link_Gốc_Instagram_Hoặc_TikTok)  
**Mạch ý tưởng:** [Chủ Đề 1](https://ytuong.fedu.vn/?q=chu-de-1) • [Chủ Đề 2](https://ytuong.fedu.vn/?q=chu-de-2)

**TRỤC KỊCH BẢN 3 NHỊP**  
[Nhịp 1: Mồi mắt/Hook] ➔ [Nhịp 2: Thân bài/Cú đấm thị giác] ➔ [Nhịp 3: Chốt hạ/CTA]
```
*(Lưu ý: Xóa bỏ hoàn toàn thông số rác như "Trực quan: 9:16 Vertical HD" hay "Tên tệp gốc").*

### 2. MỔ BĂNG THỰC CHIẾN (TỪNG SHOT / SLIDE — ĐÚNG 5 GẠCH ĐẦU DÒNG)
Mỗi phân cảnh (Shot) hoặc mỗi Slide (Carousel) BẮT BUỘC có tiêu đề chỉ rõ **[Hành động mấu chốt + Vì sao đắt]** (cấm dùng tiêu đề chung chung như "Medium Shot", "Close-Up"), kèm đúng 5 gạch đầu dòng:
- **🎬 Diễn biến:** 1-2 gạch đầu dòng chỉ rõ Ai làm gì, ở đâu (dựa trên bối cảnh thật của video, cấm bịa).
- **✅ Điểm sáng:** 1 gạch đầu dòng chốt hạ lý do khung hình hiệu quả.
- **⚠️ Điểm yếu:** 1 gạch đầu dòng chỉ ra điểm gợn hoặc điểm cần khắc phục (nếu có, khách quan, không khen 1 chiều).
- **💡 Bài học:** 1 gạch đầu dòng chốt kinh nghiệm thực chiến cho người làm video.
- **⚙️ Kỹ thuật:** 1 dòng tổng hợp nhanh: `Góc máy | Ánh sáng | Chuyển cảnh / Kỹ thuật`.

### 3. TÍCH HỢP MEGA PROMPT ÁNH XẠ 1-CHẠM (ZERO-FRICTION STORYBOARD)
Cuối báo cáo, luôn chốt bằng khối gọi ý chuyển thể:
```markdown
### ⚡ MEGA PROMPT ÁNH XẠ 1-CHẠM (ZERO-FRICTION STORYBOARD)
📸 **Thả 1 tấm ảnh chỗ bạn định quay vào đây, hoặc gõ nhanh 3 từ khóa (Ví dụ: Spa - Khách - Lọ Serum / Quán Ăn - Bếp - Món Nóng)**. Tôi sẽ nội suy đồ vật và đẻ ra thẳng Bảng Phân Cảnh (Storyboard) áp dụng ngay công thức này cho bạn quay ngay!
```

### 4. KHỐI LIÊN KẾT TƯ LIỆU DƯỚI ĐÁY (BOTTOM ASSET BLOCK)
Đặt gọn ở cuối cùng:
- 📂 **Thư mục trên máy:** `[local_path]`
- 🎬 **Video gốc:** `[video_file]`
- 🔗 **Google Drive:** `[gdrive_link]` (nếu có)
- 🌐 **Xem Báo Cáo Web:** `https://ytuong.fedu.vn/reports/[report_name].html` (khi đã sync xong)

---

## BƯỚC 4: ĐỒNG BỘ MEDIA & DEPLOY CLOUDFLARE PAGES (CHẠY NGẦM)

Khi script hoàn tất phân tích, tự động thực thi chuỗi đồng bộ:
1. **Upload ảnh & video lên R2 CDN**:
   - Ảnh keyframe: `rclone copy <shots_dir> r2:vietndjmedia/images/[folder_name]/ -v`
   - Video gốc: `rclone copy <video_mp4> r2:vietndjmedia/videos/ -v`
2. **Cập nhật CSDL YTUONG HUB**:
   - Thêm bản ghi vào `scene.html` và `master_classifications.json` (ở `/Users/vietmac/Documents/CODE/ytuong-fedu-vn`).
   - Rebuild data: `python3 /Users/vietmac/Documents/CODE/ytuong-fedu-vn/build_ideas_bank.py`.
3. **Deploy Cloudflare Pages & Git Push**:
   ```bash
   cd /Users/vietmac/Documents/CODE/ytuong-fedu-vn
   npx wrangler deploy --assets=dist --name ytuong-fedu-vn
   git add . && git commit -m "feat: sync analysis to YTUONG hub" && git push origin main
   ```
