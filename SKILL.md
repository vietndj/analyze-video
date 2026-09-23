---
name: analyze-video
description: "Kích hoạt khi người dùng gửi link video (Instagram Reels, TikTok, YouTube Shorts, FB Video) hoặc yêu cầu phân tích video, bóc tách phân cảnh, mổ xẻ kịch bản video thực chiến."
---

# KỸ NĂNG PHÂN TÍCH & BÓC TÁCH VIDEO THỰC CHIẾN (ANALYZE VIDEO SKILL)

## 📌 NGUYÊN TẮC VÀNG VỀ TÍNH NHẤT QUÁN (THE 1:1 CONSISTENCY LAW)

1. **ĐỒNG BỘ 1:1 GIỮA CHAT VÀ BÁO CÁO WEB (CLOSED-LOOP VISION SYNC)**:
   - Báo cáo trong Chat và Báo cáo Web HTML trên `ytuong.fedu.vn` **BẮT BUỘC PHẢI KHỚP NHAU 100% VỀ MẶT NỘI DUNG**.
   - **CẤM TUYỆT ĐỐI**: Để file HTML báo cáo tồn tại văn mẫu heuristic của OpenCV (*"Cận Cảnh Chi Tiết Cảm Xúc..."* hay phân loại sai thành Talking Head/Kiến trúc do bắt nhầm từ khóa).
   - Mọi phân tích chuyên sâu mà Mắt Thần AI (Vision) nhìn thấy từ ảnh chụp đều phải được ghi đè ngược vào `shot_info.json` và render lại vào file HTML trước khi hoàn tất nhiệm vụ.

2. **ƯU TIÊN TRẢ KẾT QUẢ VÀO CHAT NGAY (ZERO LATENCY)**:
   - Khi có link video, trích xuất khung hình và soi ảnh bằng `view_file`.
   - Xuất bản ngay báo cáo theo chuẩn **Gạch Đầu Dòng Tối Giản (5 ý/shot)** vào chat.

3. **TIẾN TRÌNH HẠ TẦNG & ĐỒNG BỘ NGẦM**:
   - Tải video, render webp, upload R2, Google Drive, và tái tạo file HTML chạy ngầm bằng script tự động.
   - Luôn tự động commit & push git theo quy tắc hệ thống.

---

## 📌 QUY TRÌNH THỰC THI 4 BƯỚC KHÉP VÒNG (4-STEP CLOSED-LOOP)

### BƯỚC 1: KIỂM TRA TRÙNG LẶP (PRE-CHECK DUPLICATION)
Trước khi tải hay bóc tách, kiểm tra xem video này đã có trong `scene.html` chưa:
```bash
python3 "/Users/vietmac/Documents/CODE/Quản gia/check_scene_duplicate.py" "<SHORTCODE_HOẶC_LINK>"
```
- **NẾU ĐÃ CÓ (`exists: true`)**:
  - Dừng ngay việc tải lại hay tạo thư mục mới.
  - Báo ngay cho người dùng link báo cáo Web và Drive, tóm tắt 3 dòng nội dung cốt lõi và kết thúc.
- **NẾU CHƯA CÓ (`exists: false`)**:
  - Chuyển sang Bước 2.

---

### BƯỚC 2: BÓC TÁCH TƯ LIỆU THÔ BẰNG SCRIPT
Chạy script phân tích và trích xuất khung hình:
```bash
python3 "/Users/vietmac/Documents/CODE/analyze-video/analyze_and_upload.py" "<LINK>"
```
Script sẽ tự động:
1. Tải video master về local (`/Users/vietmac/Documents/CODE/Quản gia/output_packages/<folder_name>/`).
2. Băm nhỏ các shot, trích xuất ảnh `.jpg` và `.webp` vào thư mục `extracted_shots/`.
3. Upload video và keyframe lên Cloudflare R2 CDN và Google Drive.

---

### BƯỚC 3: MẮT THẦN AI SOI ẢNH & XUẤT BẢN TRONG CHAT
AI gọi công cụ `view_file` mở trực tiếp các file ảnh `shot_XX_mid.jpg` để thực sự **NHÌN THẤY** bối cảnh, chữ text trên video, đồ vật, hành vi của nhân vật.

Toàn bộ báo cáo trong chat tuân thủ đúng 4 phần:
1. **TIÊU ĐỀ & LIÊN KẾT ĐIỀU HƯỚNG:**
   ```markdown
   # [Tên Đòn Bẩy Thị Giác / Kỹ Thuật Đắt Giá Nhất Của Video]
   **Nguồn:** [@Tên_Creator](Link_Gốc_Instagram_Hoặc_TikTok)  
   **Mạch ý tưởng:** [Chủ Đề 1](https://ytuong.fedu.vn/?q=chu-de-1) • [Chủ Đề 2](https://ytuong.fedu.vn/?q=chu-de-2)

   **TRỤC KỊCH BẢN 3 NHỊP**  
   [Nhịp 1: Mồi mắt/Hook] ➔ [Nhịp 2: Thân bài/Cú đấm thị giác] ➔ [Nhịp 3: Chốt hạ/CTA]
   ```
2. **MỔ BĂNG TỪNG SHOT (ĐÚNG 5 GẠCH ĐẦU DÒNG):**
   Mỗi shot có tiêu đề rõ `[Hành động mấu chốt + Vì sao đắt]`:
   - **🎬 Diễn biến:** 1-2 gạch đầu dòng chỉ rõ Ai làm gì, ở đâu (chuẩn xác theo ảnh thật).
   - **✅ Điểm sáng:** 1 gạch đầu dòng chốt hạ lý do khung hình hiệu quả.
   - **⚠️ Điểm yếu:** 1 gạch đầu dòng chỉ ra điểm gợn hoặc điểm cần khắc phục.
   - **💡 Bài học:** 1 gạch đầu dòng chốt kinh nghiệm thực chiến.
   - **⚙️ Kỹ thuật:** `Góc máy | Ánh sáng | Chuyển cảnh / Kỹ thuật`.
3. **MEGA PROMPT ÁNH XẠ 1-CHẠM:**
   ```markdown
   ### ⚡ MEGA PROMPT ÁNH XẠ 1-CHẠM (ZERO-FRICTION STORYBOARD)
   📸 **Thả 1 tấm ảnh chỗ bạn định quay vào đây, hoặc gõ nhanh 3 từ khóa (Ví dụ: Spa - Khách - Lọ Serum / Quán Ăn - Bếp - Món Nóng)**. Tôi sẽ nội suy đồ vật và đẻ ra thẳng Bảng Phân Cảnh (Storyboard) áp dụng ngay công thức này cho bạn quay ngay!
   ```
4. **KHỐI LIÊN KẾT TƯ LIỆU DƯỚI ĐÁY:**
   Thư mục máy, Video gốc, Google Drive, Xem Báo Cáo Web.

---

### BƯỚC 4: ĐỒNG BỘ NGƯỢC (REVERSE SYNC) ĐẢM BẢO 100% NHẤT QUÁN
Ngay sau khi phân tích xong bằng Mắt Thần, AI **BẮT BUỘC** gọi script đồng bộ ngược để ghi đè phân tích thị giác thật vào file dữ liệu và HTML:
```bash
python3 "/Users/vietmac/Documents/CODE/analyze-video/sync_ai_analysis.py" "<FOLDER_NAME>" \
  --industry "<ID_HOẶC_TÊN_NGÀNH>" \
  --style "<ID_HOẶC_TÊN_KIỂU_QUAY>" \
  --tags "<TAG_1>, <TAG_2>, <TAG_3>" \
  --overview "<CÂU_TÓM_TẮT_OVERVIEW>"
```
*(Nếu cần cập nhật chi tiết từng shot, ghi đè trực tiếp vào `shot_info.json` trước khi chạy script)*.

Script sẽ tự động:
1. Ghi nhận dữ liệu phân tích chuẩn vào `shot_info.json`.
2. Tạo lại file HTML báo cáo hoàn toàn sạch văn mẫu, đúng 100% với Chat.
3. Đồng bộ sang `vietndj.github.io/reports/` và `ytuong-fedu-vn/reports/`.
4. Cập nhật `master_classifications.json` đúng ngành nghề, kiểu quay, tags.
5. Rebuild YTUONG ideas bank (`build_ideas_bank.py`).
6. Tự động `git commit` và `git push` lên cả hai kho mã nguồn.
