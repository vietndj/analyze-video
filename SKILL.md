---
name: analyze-video
description: Kỹ năng phân tích video short-form chuyên sâu dành riêng cho Instagram Reels, Instagram Carousel đa video/album, TikTok, Facebook Video/Reels hoặc tệp video MP4 cục bộ. Bóc tách phân cảnh chuyên sâu (Shot Breakdown) với tiêu đề là điểm hiệu quả nhất + vì sao, mô tả đối tượng diễn biến, đánh giá bố cục 2 chiều khen/chê khách quan, bài học thực chiến ngắn gọn, xuất Báo Cáo Đạo Diễn HTML Mobile-First tương tác cao (< 80KB) kèm Sticky Video Player, Drawer Jump Menu, Grid/Detail View, đóng gói tự động lên Google Drive và Cloudflare R2 CDN, cập nhật fedu.vn/scene.html.
---

# KỸ NĂNG PHÂN TÍCH VIDEO & CAROUSEL SERIES CHUYÊN SÂU (ANALYZE VIDEO SKILL)

## 📌 QUY TẮC ĐỊNH TUYẾN LINK TỰ ĐỘNG (SMART URL ROUTING)
- **Áp dụng cho**: Đường link **Instagram** (`instagram.com/reel/`, `instagram.com/p/`, `instagram.com/tv/`), **TikTok** (`tiktok.com`), **Facebook Video/Reels** (`facebook.com`, `fb.watch`) hoặc tệp video `.mp4` cục bộ.
- **TUYỆT ĐỐI LOẠI TRỪ YOUTUBE**: Nếu người dùng gửi link **YouTube** (`youtube.com`, `youtu.be`), **BẮT BUỘC** chuyển sang kỹ năng **`phan-tich-podcast-youtube`** (phân tích podcast dài Kiến trúc sư Trí tuệ Hệ thống), TUYỆT ĐỐI KHÔNG dùng `analyze-video` để bóc tách OpenCV video YouTube.

---

Khi người dùng gửi một đường link video ngắn (Instagram Reels, TikTok, Facebook Video, bài đăng Instagram Carousel đa video) hoặc tệp video MP4 cục bộ, Agent BẮT BUỘC thực hiện quy trình tự động sau:

## 1. TỰ ĐỘNG NHẬN DIỆN & TẢI TOÀN BỘ TÀI NGUYÊN (INGESTION)
- Sử dụng `yt-dlp` quét đường link:
  - **Trường hợp 1 (Video đơn lẻ - Reel / TikTok / Shorts)**: Tải video gốc `.mp4` và tách file âm thanh `.mp3`.
  - **Trường hợp 2 (Bài đăng Carousel đa video / Album)**: Tự động tải TOÀN BỘ tất cả các slide video (`slide_01.mp4`, `slide_02.mp4`,...) vào thư mục `carousel_slides/`.
- Tự động tạo thư mục đóng gói chuẩn hóa:
  `Work/AI_Video_Analysis/IG_@[Tên_Kênh]_[Mã_Bài]_[Phân_Loại]/`

## 2. PHÂN TÍCH SHOTS & TRÍCH XUẤT KEYFRAME (OPENCV)
- **Với Video đơn lẻ**:
  - Chạy thuật toán OpenCV HSV Histogram phát hiện toàn bộ các điểm cắt cảnh (Scene Cuts).
  - Trích xuất 3 ảnh Keyframe cho mỗi Shot (`shot_XX_start.jpg`, `shot_XX_mid.jpg`, `shot_XX_end.jpg`).
  - Tạo ảnh ghép so sánh chuyển cảnh `trans_XX_to_YY.jpg`.
- **Với Album Carousel (Nhiều Video)**:
  - Phân tích chi tiết từng Slide Video: độ phân giải, thời lượng, vai trò giữ chân trong chuỗi (Hook -> Movement -> Detail -> Fast-cut -> Context -> CTA).
  - Trích xuất các khung hình đại diện của từng Slide (`slide_XX_mid.jpg`, `slide_XX_start.jpg`, `slide_XX_end.jpg`).

## 3. QUY CHUẨN BÓC TÁCH PHÂN CẢNH CHI TIẾT (SHOT BREAKDOWN STANDARDS)
Mỗi phân cảnh (Shot) khi phân tích và xuất bản báo cáo BẮT BUỘC phải bóc tách dựa trên sự thật bối cảnh video (đọc caption, phân tích audio thoại và hình ảnh thật, TUYỆT ĐỐI KHÔNG DÙNG VĂN MẪU/TEMPLATE ẢO), bao gồm:

1. **TIÊU ĐỀ PHÂN CẢNH (SHOT HEADLINE / KEY VISUAL LOGIC)**:
   - **BẮT BUỘC**: Đặt trực tiếp **Điểm hiệu quả nhất / Logic thị giác đắt giá nhất trong shot đó + Lý do vì sao** làm tiêu đề chính.
   - **TUYỆT ĐỐI KHÔNG** dùng tên góc máy chung chung (như *"Medium Shot"*, *"Close-Up"*, *"Góc quay cận vừa"*) làm tiêu đề.
   - *Ví dụ chuẩn*:
     - *"Hook thị giác 'Creators are annoying': Khóa sự chú ý bằng tách lớp chủ thể qua cốc nước và màn hình điện thoại"*
     - *"Nén tiêu cự Telephoto 3x (50MP): Bắt trọn cảm xúc biểu cảm khuôn mặt và ánh mắt người ngồi đối diện"*
     - *"Bố cục 3 Picture Collage (0.6x - 1x - 3x): Trình bày đa góc nhìn trong cùng một khoảnh khắc"*

2. **MÔ TẢ ĐỐI TƯỢNG & DIỄN BIẾN (SUBJECT & ACTION)**:
   - Mô tả cụ thể đối tượng trong cảnh là ai / cái gì?
   - Cảnh đó diễn tả điều gì, hành động diễn ra như thế nào trong khoảng thời gian đó, bám sát nội dung thực tế của video.

3. **ĐÁNH GIÁ BỐ CỤC & PHÊ BÌNH THỊ GIÁC 2 CHIỀU (COMPOSITION CRITIQUE - CẢ TỐT VÀ XẤU)**:
   - **Điểm hiệu quả (Mặt tốt / Ưu điểm)**: Phân tích tỷ lệ khung hình, điểm nhấn thị giác, hướng dẫn mắt, sự kết hợp ánh sáng và màu sắc mang lại hiệu ứng gì.
   - **Điểm hạn chế / Cần lưu ý (Mặt chưa tốt / Nhược điểm)**: Phê bình khách quan và thẳng thắn (bố cục bị chật chội, tiền cảnh vướng vật thể thừa, ánh sáng bị bết vùng tối, chuyển động camera hơi giật, cắt cảnh hơi gắt...). **TUYỆT ĐỐI KHÔNG KHEN MỘT CHIỀU**.

4. **BÀI HỌC ĐÚC KẾT NGẮN GỌN (ACTIONABLE TAKEAWAY)**:
   - Rút ra 1-2 câu súc tích, thực chiến: Người làm video / đạo diễn / creator học được kỹ thuật hoặc tư duy gì từ shot này để áp dụng vào tác phẩm của mình.

5. **THÔNG SỐ KỸ THUẬT QUAY DỰNG**:
   - Mốc thời gian & Thời lượng chính xác (`0.00s - 2.67s (2.67s)`).
   - Bối cảnh / Vị trí quay thực tế.
   - Góc máy & Tiêu cự ống kính ước tính (VD: `Ultra-wide 0.6x (16mm)`, `Telephoto 3x (85mm)`).
   - Ánh sáng & Bảng màu (Color Grading).
   - Kỹ thuật chuyển tiếp sang cảnh tiếp theo (Transition Technique).
   *(LƯU Ý: KHÔNG sinh AI Prompt / Runway Prompt)*.

## 4. ĐỒNG BỘ HÌNH ẢNH VÀO THƯ MỤC ARTIFACTS
- Sao chép toàn bộ ảnh trích xuất sang thư mục Artifacts của phiên làm việc:
  `<appDataDir>/brain/<conversation-id>/extracted_shots/`
- Mọi hình ảnh nhúng vào báo cáo chat đều sử dụng cú pháp: `![Tên ảnh](file://<appDataDir>/brain/<conversation-id>/extracted_shots/...)`.

## 5. XUẤT BẢN BÁO CÁO HTML MOBILE-FIRST TƯƠNG TÁC CAO (KHÔNG XUẤT PDF)
- **QUY TẮC CỐT LÕI**: TUYỆT ĐỐI KHÔNG XUẤT FILE PDF để tối ưu tốc độ xử lý, tiết kiệm bộ nhớ và tập trung 100% vào trải nghiệm tương tác Web hiện đại.
- **BẮT BUỘC CHUẨN GIAO DIỆN MOBILE-FIRST & DESKTOP SPLIT-SCREEN**:
  - **Sticky Video Player**:
    - Trên Di Động (Mobile): Ghim cố định ở đỉnh màn hình hoặc chế độ Mini Player khi cuộn.
    - Trên Máy Tính (Desktop): Bố cục chia đôi (Split-Screen) - Cột trái cố định Video Player lớn kèm bộ điều khiển, Cột phải cuộn đọc phân tích chi tiết.
  - **Bộ điều khiển Đạo Diễn chuyên sâu**:
    - Tua chậm tốc độ: 0.25x (Match Cut), 0.5x, 1.0x, 1.5x, 2.0x.
    - Tua từng khung hình: Prev 1 Frame / Next 1 Frame.
    - Bật/Tắt tiếng, Loop lặp đoạn, Tải video gốc.
  - **Auto-Sync & Timestamp Jump**:
    - Mọi mốc thời gian (VD: `[2.57s - 5.37s]` hoặc nút Play `2.57s`) khi click đều lập tức nhảy video player đến đúng mốc giây phân cảnh.
    - Click vào bất kỳ ảnh thumbnail nào cũng lập tức phát video phân cảnh đó.
  - **Bộ Chuyển Đổi Chế Độ Xem (View Switcher)**:
    - Chế độ Storyboard Chi Tiết (Detail View): Thẻ phân tích ánh sáng, góc máy, prompt AI, điểm tốt/xấu, bài học.
    - Chế độ Lưới Ảnh (Visual Grid View): Lưới ảnh Keyframe để quan sát nhịp điệu ánh sáng và màu sắc tổng thể.
  - **Mục Lục Trượt Nhanh (Drawer / Jump Menu)**:
    - Nút mở Drawer danh sách toàn bộ phân cảnh để nhảy tức thì đến bất kỳ shot nào mà không phải cuộn mỏi tay.
  - **Lightbox Modal Darkroom**:
    - Click vào bất kỳ ảnh nào để mở trình xem ảnh toàn màn hình với caption phân cảnh, hỗ trợ phím ESC đóng, phím mũi tên hoặc vuốt để chuyển ảnh.
  - **Thẻ Phân Cảnh Trực Quan Hóa 3 Khối Độc Lập**:
    - Khối Tiêu Đề Logic & Mô tả Đối tượng diễn biến.
    - Khối Đánh giá Bố Cục: `✅ Điểm sáng thị giác` vs `⚠️ Hạn chế / Điểm cần khắc phục`.
    - Khối Đúc kết Thực chiến: `💡 Bài học áp dụng`.
- **BẮT BUỘC CHUẨN FONT DỰ ÁN**:
  - Tiêu đề & Đề mục: `Plus Jakarta Sans` / `SVN-Aeonik`.
  - Thân bài & Đọc: `Be Vietnam Pro` / `GT America`.
- **BẮT BUỘC NÚT XEM INSTAGRAM GỐC GẮN VÀO TÊN TÁC GIẢ**:
  - Tại phần Header thông tin tác giả (`.meta-tags-flex`), tên tác giả BẮT BUỘC phải được gắn trực tiếp đường link/nút bấm mở bài post hoặc profile Instagram gốc (`target="_blank"`, class `.author-ig-badge` kèm nút `📸 Xem Instagram Gốc ↗`).
- **SIÊU NHẸ (< 80KB)**:
  - Tất cả ảnh và video BẮT BUỘC nhúng trực tiếp qua URL Cloudflare R2 CDN (`https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/...`).
  - TUYỆT ĐỐI KHÔNG NHÚNG CHUỖI BASE64.

## 6. ĐÓNG GÓI THƯ MỤC DỰ ÁN & TỰ ĐỘNG UPLOAD LÊN GOOGLE DRIVE
- Quy tắc đặt tên tệp BẮT BUỘC:
  `[Tên_Chủ_Đề_Nội_Dung] - @[Tên_Kênh_Insta].html`
  `[Tên_Chủ_Đề_Nội_Dung] - @[Tên_Kênh_Insta].mp4`
- Đóng gói toàn bộ tài nguyên:
  `Work/AI_Video_Analysis/[Tên_Thư_Mục_Package]/`
  ├── `[Nội_Dung] - @[Tên_Kênh].mp4` (hoặc `carousel_slides/`)
  ├── `[Nội_Dung] - @[Tên_Kênh].html`
  ├── `shot_info.json` (hoặc `carousel_info.json`)
  └── `extracted_shots/` (Chứa toàn bộ Keyframes & Transitions)
- Chạy lệnh Rclone tự động đồng bộ lên Google Drive:
  `rclone copy output_packages/... gdrive:Work/AI_Video_Analysis/... -v`
- Lấy đường link chia sẻ trực tiếp của Thư Mục (Folder) từ Google Drive qua `rclone link`.

## 7. TỰ ĐỘNG ĐỒNG BỘ MEDIA LÊN CLOUDFLARE R2 & GITHUB PAGES
- Tải Media lên Cloudflare R2 CDN:
  - Video: `rclone copy <Đường_Dẫn_Video_MP4> r2:vietndjmedia/videos/ -v`
  - Ảnh: `rclone copy <Thư_Mục_extracted_shots> r2:vietndjmedia/images/[Tên_Thư_Mục_Gói]/ -v`
- Bổ sung vào cơ sở dữ liệu `scene.html` và kho báo cáo:
  - Sao chép báo cáo HTML vào `reports/[Tên_Chủ_Đề] - @[Tên_Kênh].html`.
  - Thêm đối tượng mới vào mảng `portalData` ở đầu danh sách trong file `scene.html`.
  - Thực hiện lệnh `git add scene.html reports/ && git commit -m "feat: add analysis for [Tên_Video]" && git push origin master` để cập nhật online ngay lập tức.

## 8. TRÌNH BÀY KẾT QUẢ CHO NGƯỜI DÙNG
- Quy tắc cốt lõi về trình bày:
  - Tuyệt đối KHÔNG dùng đường kẻ ngang (`---`).
  - Đảm bảo độ thoáng và nhịp thở thị giác: Luôn sử dụng khoảng cách dòng chuẩn (`\n\n`) giữa các đoạn văn.
  - Bố cục nội dung chuyên nghiệp:
    - Phần 1: Thông số tổng quan video.
    - Phần 2: Phân tích nghệ thuật thị giác & Ngôn ngữ điện ảnh (Ánh sáng, Góc máy, Nhịp dựng).
    - Phần 3: Bảng bóc tách phân cảnh tiêu biểu (Storyboard) có nhúng ảnh Keyframe minh họa trực tiếp, đầy đủ tiêu đề đắt giá, mô tả đối tượng, đánh giá tốt/xấu và bài học rút ra.
    - Phần 4: Kịch bản thực chiến ứng dụng (Shooting Script).
  - ĐẶT KHỐI LIÊN KẾT XUỐNG CUỐI CÙNG (BOTTOM LINKS BLOCK):
    - `[Mở trong Finder (Thư mục gói dự án)](file:///Users/vietmac/.../output_packages/...)`
    - `[Mở Báo Cáo HTML trong máy](file:///Users/vietmac/.../output_packages/.../...)`
    - `[Mở File Video MP4 trong máy](file:///Users/vietmac/.../output_packages/.../...)`
    - `[Mở Thư Mục Google Drive ↗](https://drive.google.com/...)`
    - `[Mở Cổng Tra Cứu Điện Ảnh Trực Tuyến ↗](https://vietndj.github.io/scene.html)`

## 9. THÔNG BÁO VỀ TELEGRAM (@phantichVideoInsta_bot HOẶC @viet_vni_bot) - BẮT BUỘC TRUYỀN --cid
- Mặc định: KHÔNG tự ý bắn Telegram nếu anh Việt chat trực tiếp trên Antigravity, trừ khi anh Việt yêu cầu gửi Telegram / báo qua bot hoặc nhiệm vụ được kích hoạt từ daemon (@phantichVideoInsta_bot).
- **BẮT BUỘC CÓ CỜ `--cid "$ANTIGRAVITY_CONVERSATION_ID"`**: Để tin nhắn Telegram tự động gắn link clickable `💬 Mở Antigravity` (dẫn tới `https://fedu.vn/course/open.html?c={CID}`), giúp anh Việt trên iPhone/Mac nhấp 1 chạm là nhảy thẳng vào đúng luồng hội thoại tương ứng trên Antigravity IDE.
- **Câu lệnh chuẩn**:
  ```bash
  python3 "/Users/vietmac/Documents/CODE/Quản gia/telegram_notify.py" --bot analyze --msg "🎬 <b>HOÀN TẤT PHÂN TÍCH ĐIỆN ẢNH: [Tên_Video]</b>\n━━━━━━━━━━━━━━━━━━\n📁 <b>Thư mục Google Drive:</b> [Link_Folder]\n🌐 <b>Xem Báo Cáo Tương Tác:</b> https://ytuong.fedu.vn/reports/[Tên_Báo_Cáo].html\n✨ Đã bóc tách [N] phân cảnh chuẩn logic đắt giá, mô tả đối tượng, đánh giá 2 chiều và bài học thực chiến!" --cid "$ANTIGRAVITY_CONVERSATION_ID"
  ```
- *Lưu ý*: Nếu chạy từ bot cảnh báo alert (@viet_vni_bot), đổi `--bot analyze` thành `--bot alert`. Luôn luôn giữ `--cid "$ANTIGRAVITY_CONVERSATION_ID"`.
