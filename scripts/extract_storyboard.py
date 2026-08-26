#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import re
import shutil
import base64
from pathlib import Path

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GDRIVE_LOCAL_SYNC = "/Users/vietmac/Library/CloudStorage/GoogleDrive-vietnd5@gmail.com/My Drive/AI_Video_Analysis"
GDRIVE_REMOTE_BASE = "gdrive:AI_Video_Analysis"

def run_cmd(cmd):
    """Run shell command and return returncode, stdout, stderr."""
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def sanitize_filename(name):
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r'\s+', "_", clean)
    return clean[:50].strip("._")

def get_video_info(url_or_path):
    """Get metadata using yt-dlp."""
    if os.path.isfile(url_or_path):
        return {
            "id": Path(url_or_path).stem,
            "uploader": "local_user",
            "title": Path(url_or_path).stem,
            "webpage_url": url_or_path,
            "duration": 15.0
        }
    
    cmd = f'yt-dlp --cookies-from-browser safari --no-warnings --dump-json "{url_or_path}"'
    code, out, _ = run_cmd(cmd)
    if code != 0 or not out:
        cmd = f'yt-dlp --no-warnings --dump-json "{url_or_path}"'
        code, out, _ = run_cmd(cmd)
    if code == 0 and out:
        try:
            data = json.loads(out)
            return {
                "id": data.get("id", "video"),
                "uploader": data.get("uploader") or data.get("uploader_id") or data.get("channel") or "instagram_user",
                "title": data.get("title", "video_reel"),
                "description": data.get("description", ""),
                "webpage_url": data.get("webpage_url", url_or_path),
                "duration": data.get("duration", 15.0)
            }
        except Exception:
            pass
    return {
        "id": "reel",
        "uploader": "instagram_user",
        "title": "Instagram_Video",
        "webpage_url": url_or_path,
        "duration": 15.0
    }

def get_video_duration(video_path):
    cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
    code, out, _ = run_cmd(cmd)
    try:
        return float(out)
    except Exception:
        return 15.0

def get_video_dimensions(video_path):
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{video_path}"'
    code, out, _ = run_cmd(cmd)
    try:
        parts = out.strip().split('x')
        return int(parts[0]), int(parts[1])
    except Exception:
        return 1080, 1920

def extract_frame(video_path, timestamp, output_path):
    cmd = f'ffmpeg -y -ss {timestamp:.2f} -i "{video_path}" -vframes 1 -q:v 2 "{output_path}"'
    run_cmd(cmd)
    return os.path.exists(output_path)

def image_to_base64(img_path):
    if not os.path.exists(img_path):
        return ""
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

def generate_pdf_report(meta, frames, output_dir, analysis_data=None):
    """Generate modern PDF report from HTML."""
    pdf_path = os.path.join(output_dir, "Storyboard_Analysis.pdf")
    html_path = os.path.join(output_dir, "Storyboard_Analysis.html")

    # Prepare frame cards HTML
    cards_html = ""
    for f in frames:
        b64 = image_to_base64(f["path"])
        cards_html += f"""
        <div class="frame-card">
            <div class="frame-img-box">
                <img src="{b64}" alt="{f['filename']}">
                <span class="timestamp-badge">{f['timestamp_sec']}s</span>
            </div>
            <div class="frame-content">
                <div class="frame-title">{f['description']}</div>
                <div class="frame-details">
                    <p><strong>Góc máy:</strong> {f.get('shot_type', 'Cận cảnh / Khung dọc 9:16')}</p>
                    <p><strong>Nội dung:</strong> {f.get('visual_action', 'Hành động chuyển động nhanh tạo điểm dừng thị giác.')}</p>
                    <p><strong>Lời thoại:</strong> <em>"{f.get('dialogue', '...')}"</em></p>
                </div>
            </div>
        </div>
        """

    title_safe = meta.get('title', 'Phân Tích Video Storyboard')
    uploader = meta.get('uploader', 'instagram_creator')
    url = meta.get('webpage_url', '')
    duration = meta.get('duration_seconds', 15.0)
    aspect = meta.get('aspect_ratio', '9:16')

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Phân Tích Storyboard Video</title>
<style>
    @font-face {{
        font-family: 'SVN-Aeonik';
        src: url('file:///d:/CODE%20on%20window/Qu%E1%BA%A3n%20gia/fonts/SVN-AEONIK-REGULAR.TTF') format('truetype');
        font-weight: 400;
    }}
    @font-face {{
        font-family: 'SVN-Aeonik';
        src: url('file:///d:/CODE%20on%20window/Qu%E1%BA%A3n%20gia/fonts/SVN-AEONIK-BOLD.TTF') format('truetype');
        font-weight: 700;
    }}
    @font-face {{
        font-family: 'SVN-Acta';
        src: url('file:///d:/CODE%20on%20window/Qu%E1%BA%A3n%20gia/fonts/SVN-Acta-Bold.ttf') format('truetype');
        font-weight: 700;
    }}
    
    * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-family: 'SVN-Aeonik', sans-serif !important;
    }}
    body {{
        font-family: 'SVN-Aeonik', sans-serif;
        color: #0f172a;
        background: #f8fafc;
        padding: 32px;
        line-height: 1.5;
        -webkit-print-color-adjust: exact;
    }}
    h1, h2, .section-title {{
        font-family: 'SVN-Aeonik', 'SVN-Acta', sans-serif !important;
    }}
    .header {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }}
    .badge {{
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        font-weight: 700;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}
    h1 {{
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 12px;
    }}
    .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 16px;
        background: #f1f5f9;
        padding: 12px 16px;
        border-radius: 10px;
        font-size: 12px;
    }}
    .meta-item strong {{
        color: #475569;
        display: block;
        font-size: 11px;
        margin-bottom: 2px;
    }}
    .meta-item span {{
        color: #0f172a;
        font-weight: 600;
        word-break: break-all;
    }}
    .section-title {{
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        margin: 28px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .section-title::before {{
        content: '';
        display: inline-block;
        width: 4px;
        height: 18px;
        background: #2563eb;
        border-radius: 2px;
    }}
    .hook-box {{
        background: #ffffff;
        border-left: 4px solid #ef4444;
        border-radius: 0 12px 12px 0;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        font-size: 13px;
    }}
    .hook-box h3 {{
        color: #b91c1c;
        font-size: 14px;
        margin-bottom: 6px;
    }}
    .storyboard-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }}
    .frame-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        page-break-inside: avoid;
    }}
    .frame-img-box {{
        position: relative;
        width: 100%;
        height: 220px;
        background: #000000;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .frame-img-box img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }}
    .timestamp-badge {{
        position: absolute;
        bottom: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.75);
        color: #ffffff;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
    }}
    .frame-content {{
        padding: 14px 16px;
        flex: 1;
    }}
    .frame-title {{
        font-size: 13px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
    }}
    .frame-details p {{
        font-size: 12px;
        color: #475569;
        margin-bottom: 4px;
    }}
    .frame-details em {{
        color: #0f172a;
        font-weight: 500;
    }}
    .remake-box {{
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 24px;
        font-size: 13px;
        page-break-inside: avoid;
    }}
    .remake-box h3 {{
        color: #166534;
        font-size: 14px;
        margin-bottom: 8px;
    }}
    .remake-box ul {{
        margin-left: 20px;
        color: #15803d;
    }}
    .remake-box li {{
        margin-bottom: 4px;
    }}
</style>
</head>
<body>

<div class="header">
    <div class="badge">Báo Cáo Phân Tích Storyboard Video</div>
    <h1>{title_safe}</h1>
    <div class="meta-grid">
        <div class="meta-item">
            <strong>Kênh Creator</strong>
            <span>@{uploader}</span>
        </div>
        <div class="meta-item">
            <strong>Thời Lượng</strong>
            <span>{duration}s</span>
        </div>
        <div class="meta-item">
            <strong>Tỷ Lệ Video</strong>
            <span>{aspect}</span>
        </div>
        <div class="meta-item">
            <strong>Link Gốc</strong>
            <span><a href="{url}" target="_blank" style="color:#2563eb; text-decoration:none;">Xem trên Instagram ↗</a></span>
        </div>
    </div>
</div>

<div class="hook-box">
    <h3>🎯 Phân Tích Công Thức 3 Giây Đầu (The 3-Second Hook Rule)</h3>
    <p><strong>Visual Hook:</strong> Mở màn bằng khung hình cận cảnh có chuyển động tức thì (tương tác trực diện ống kính hoặc đồ vật bất thường), loại bỏ 100% phần thừa mở đầu.</p>
    <p><strong>Tâm lý giữ chân:</strong> Đánh thẳng vào nỗi sợ bỏ lỡ (FOMO) hoặc sự tò mò trong 1.5s đầu tiên trước khi người xem kịp quẹt qua video khác.</p>
</div>

<div class="section-title">Bóc Tách Khung Hình Phân Cảnh (Storyboard Breakdown)</div>

<div class="storyboard-grid">
    {cards_html}
</div>

<div class="remake-box">
    <h3>💡 Hướng Dẫn Remake Chuyển Thể Sang Sản Phẩm Của Bạn</h3>
    <ul>
        <li><strong>Đúp 1 (0s - 3s):</strong> Giữ nguyên nhịp điệu và cỡ cảnh cận của video mẫu, chỉ thay gương mặt/sản phẩm của bạn vào.</li>
        <li><strong>Đúp 2 (Thân bài):</strong> Cắt nhịp mỗi 1.2s - 1.8s/cut để giữ nhịp mắt, lồng tiếng dứt khoát không có từ thừa (à, ừ, thì, là).</li>
        <li><strong>Đúp 3 (CTA cuối):</strong> Đặt lời kêu gọi hành động trực tiếp kèm chỉ dẫn bấm vào giỏ hàng hoặc comment từ khóa.</li>
    </ul>
</div>

</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Convert to PDF via Headless Chrome
    cmd_pdf = f'"{CHROME_BIN}" --headless=new --disable-gpu --print-to-pdf="{pdf_path}" --no-pdf-header-footer "{html_path}"'
    run_cmd(cmd_pdf)

    return pdf_path if os.path.exists(pdf_path) else None

def upload_and_get_link(local_folder_path, folder_name):
    """Sync to local Google Drive mount and upload via rclone to get public link."""
    # 1. Sync to local Google Drive mount (Fast macOS native sync)
    target_local_drive = os.path.join(GDRIVE_LOCAL_SYNC, folder_name)
    os.makedirs(GDRIVE_LOCAL_SYNC, exist_ok=True)
    if os.path.exists(target_local_drive):
        shutil.rmtree(target_local_drive)
    shutil.copytree(local_folder_path, target_local_drive)
    print(f"[*] Copied to local Google Drive mount: {target_local_drive}", file=sys.stderr)

    # 2. Upload via rclone to ensure it's on cloud & get link
    remote_folder = f"{GDRIVE_REMOTE_BASE}/{folder_name}"
    cmd_upload = f'rclone copy "{local_folder_path}" "{remote_folder}"'
    run_cmd(cmd_upload)

    # 3. Get share link
    cmd_link = f'rclone link "{remote_folder}"'
    code, out, _ = run_cmd(cmd_link)
    
    gdrive_link = out.strip() if code == 0 and "http" in out else ""
    return gdrive_link

def process_video_pipeline(url_or_path, output_base=None):
    if not output_base:
        output_base = os.path.abspath(os.path.join(os.getcwd(), "storyboard_output"))
    os.makedirs(output_base, exist_ok=True)

    # Step 1: Get metadata
    print("[*] 1. Extracting video metadata...", file=sys.stderr)
    info = get_video_info(url_or_path)
    
    uploader_clean = sanitize_filename(info.get("uploader", "instagram_creator"))
    shortcode = sanitize_filename(info.get("id", "reel"))
    title_clean = sanitize_filename(info.get("title", "video"))[:30]

    # Standard Folder & Video Naming convention: IG_@username_shortcode_title
    folder_name = f"IG_@{uploader_clean}_{shortcode}_{title_clean}".strip("_")
    package_dir = os.path.join(output_base, folder_name)
    frames_dir = os.path.join(package_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Step 2: Download or copy original video
    print("[*] 2. Downloading / saving original video...", file=sys.stderr)
    video_filename = f"IG_@{uploader_clean}_{shortcode}.mp4"
    dest_video_path = os.path.join(package_dir, video_filename)

    if os.path.isfile(url_or_path):
        shutil.copy2(url_or_path, dest_video_path)
    else:
        temp_template = os.path.join(package_dir, "temp_video.%(ext)s")
        cmd_dl = f'yt-dlp --cookies-from-browser safari --no-warnings -f "b[ext=mp4]/bv*+ba/b" -o "{temp_template}" "{url_or_path}"'
        run_cmd(cmd_dl)
        
        # Rename downloaded file to standard name
        downloaded = list(Path(package_dir).glob("temp_video.*"))
        if downloaded:
            shutil.move(str(downloaded[0]), dest_video_path)
        else:
            return {"success": False, "error": "Could not download video."}

    # Step 3: Extract duration & dimensions
    duration = get_video_duration(dest_video_path)
    width, height = get_video_dimensions(dest_video_path)
    aspect_ratio = "9:16 (Dọc)" if height > width else ("16:9 (Ngang)" if width > height else "1:1 (Vuông)")

    # Step 4: Extract audio
    print("[*] 3. Extracting audio track...", file=sys.stderr)
    audio_path = os.path.join(package_dir, "audio.mp3")
    cmd_audio = f'ffmpeg -y -i "{dest_video_path}" -vn -acodec libmp3lame -q:a 3 "{audio_path}"'
    run_cmd(cmd_audio)

    # Step 5: Extract 7 key frames
    print("[*] 4. Extracting 7 keyframes for storyboard...", file=sys.stderr)
    key_timestamps = [
        ("frame_01_hook_0.5s.jpg", 0.5, "Hook mở màn (0.5s) - Giữ mắt người xem", "Cận cảnh (Close-up)", "Chuyển động dứt khoát / Đồ vật lạ"),
        ("frame_02_hook_1.5s.jpg", min(1.5, max(0.6, duration * 0.1)), "Visual Hook (1.5s) - Yếu tố kích thích", "Trung cảnh (Medium Shot)", "Biểu cảm bất ngờ / Chữ to giật tít"),
        ("frame_03_hook_3.0s.jpg", min(3.0, max(1.6, duration * 0.2)), "Hook hoàn thiện (3.0s) - Đặt vấn đề / Nỗi đau", "Cận cảnh sản phẩm/mặt", "Nhấn mạnh nỗi đau khách hàng"),
        ("frame_04_body_25pct.jpg", max(3.5, duration * 0.25), "Thân bài 1 (25%) - Triển khai tình huống", "Trung cảnh / Toàn cảnh", "Diễn giải bối cảnh thực tế"),
        ("frame_05_body_50pct.jpg", duration * 0.50, "Thân bài 2 (50%) - Giải pháp / Sản phẩm", "Cận cảnh chi tiết (Macro/Insert)", "Thao tác sử dụng sản phẩm"),
        ("frame_06_body_75pct.jpg", duration * 0.75, "Thân bài 3 (75%) - Bằng chứng / Thuyết phục", "Split-screen / Trước-Sau", "Kết quả thực tế / Review"),
        ("frame_07_cta_end.jpg", max(0.5, duration - 1.0), "CTA Kết thúc - Kêu gọi hành động", "Cận cảnh hướng dẫn", "Chỉ tay vào giỏ hàng / Comment")
    ]

    frames_info = []
    for fname, ts, desc, shot, action in key_timestamps:
        ts = min(ts, max(0.0, duration - 0.2))
        fpath = os.path.join(frames_dir, fname)
        ok = extract_frame(dest_video_path, ts, fpath)
        if ok:
            frames_info.append({
                "filename": fname,
                "timestamp_sec": round(ts, 2),
                "description": desc,
                "shot_type": shot,
                "visual_action": action,
                "path": fpath
            })

    meta = {
        "title": info.get("title", "Video Phân Tích"),
        "uploader": uploader_clean,
        "shortcode": shortcode,
        "webpage_url": info.get("webpage_url", url_or_path),
        "duration_seconds": round(duration, 2),
        "dimensions": f"{width}x{height}",
        "aspect_ratio": aspect_ratio
    }

    # Step 6: Generate PDF Report
    print("[*] 5. Generating professional PDF report...", file=sys.stderr)
    pdf_file = generate_pdf_report(meta, frames_info, package_dir)

    # Step 7: Upload to Google Drive and get Share Link
    print("[*] 6. Uploading package folder to Google Drive...", file=sys.stderr)
    gdrive_link = upload_and_get_link(package_dir, folder_name)

    result = {
        "success": True,
        "folder_name": folder_name,
        "local_package_path": package_dir,
        "gdrive_link": gdrive_link,
        "original_video_file": video_filename,
        "original_video_path": dest_video_path,
        "audio_file": "audio.mp3",
        "audio_path": audio_path,
        "pdf_report_file": "Storyboard_Analysis.pdf",
        "pdf_report_path": pdf_file,
        "frames_count": len(frames_info),
        "meta": meta,
        "frames": frames_info
    }

    # Save summary json
    with open(os.path.join(package_dir, "package_summary.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Video Storyboard, PDF & Google Drive Pipeline")
    parser.add_argument("url_or_path", help="Instagram/TikTok/YouTube link or local video path")
    parser.add_argument("--output_base", default=None, help="Base output directory")
    args = parser.parse_args()

    res = process_video_pipeline(args.url_or_path, args.output_base)
    print(json.dumps(res, ensure_ascii=False, indent=2))
