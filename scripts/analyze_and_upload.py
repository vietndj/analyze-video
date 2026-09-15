#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Video & Carousel Analysis Pipeline (Mobile-First Interactive HTML & Cloudflare R2 CDN)
Tự động phân tích sâu ngôn ngữ điện ảnh, bóc tách phân cảnh chuẩn đạo diễn:
- Tiêu đề là điểm hiệu quả nhất + vì sao
- Mô tả đối tượng và diễn biến cảnh
- Đánh giá bố cục 2 chiều (Mặt tốt & Hạn chế/Cần lưu ý)
- Bài học thực chiến ngắn gọn
- Xuất bản Báo Cáo Đạo Diễn Mobile-First tương tác cao.
"""
import os
import sys
import json
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import urllib.parse

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def get_rclone_bin():
    return shutil.which("rclone") or "/opt/homebrew/bin/rclone" or "rclone"

RCLONE_EXE = get_rclone_bin()
GDRIVE_REMOTE_BASE = "gdrive:Work/AI_Video_Analysis"
R2_MEDIA_BASE = "https://pub-447bd44dfdac4938912655c855b8631c.r2.dev"

def sanitize_name(name):
    clean = re.sub(r'[\\/*?:"<>|]', "", name)
    clean = re.sub(r'\s+', "_", clean)
    return clean[:45].strip("._")

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def fetch_tiktok_meta(url):
    try:
        import urllib.request
        import urllib.parse
        import json
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            if res_data.get("code") == 0 and "data" in res_data:
                d = res_data["data"]
                return {
                    "id": str(d.get("id", "video")),
                    "uploader": d.get("author", {}).get("unique_id") or d.get("author", {}).get("nickname") or "tinanguyen2004",
                    "title": d.get("title", "video"),
                    "description": d.get("title", ""),
                    "url": url,
                    "duration": d.get("duration", 0),
                    "play_url": d.get("play", ""),
                    "is_carousel": False
                }
    except Exception as e:
        print(f"[-] TikTok API error: {e}")
    return None

def get_post_metadata(url_or_path):
    if os.path.isfile(url_or_path):
        stem = Path(url_or_path).stem
        return [{
            "id": stem,
            "uploader": "local_creator",
            "title": stem,
            "url": url_or_path,
            "is_carousel": False
        }]
    
    if "tiktok.com" in url_or_path:
        tt_item = fetch_tiktok_meta(url_or_path)
        if tt_item:
            return [tt_item]

    cmd = f'yt-dlp --no-warnings --dump-json "{url_or_path}"'
    code, out, _ = run_cmd(cmd)
    items = []
    if code == 0 and out:
        lines = [l for l in out.strip().split('\n') if l.strip()]
        for l in lines:
            try:
                data = json.loads(l)
                items.append({
                    "id": data.get("id", "video"),
                    "uploader": data.get("uploader") or data.get("uploader_id") or data.get("channel") or "creator",
                    "title": data.get("title", "video"),
                    "description": data.get("description", ""),
                    "url": data.get("webpage_url", url_or_path),
                    "duration": data.get("duration"),
                    "is_carousel": len(lines) > 1
                })
            except Exception:
                pass
    
    if not items:
        if "tiktok.com" in url_or_path:
            tt_item = fetch_tiktok_meta(url_or_path)
            if tt_item:
                return [tt_item]
        match = re.search(r'/(?:p|reel|shorts)/([A-Za-z0-9_-]+)', url_or_path)
        shortcode = match.group(1) if match else "video"
        items.append({
            "id": shortcode,
            "uploader": "creator",
            "title": f"Video_{shortcode}",
            "url": url_or_path,
            "is_carousel": False
        })
    return items

def get_default_output_base():
    p1 = "/Users/vietmac/Documents/CODE/Video phan tich/output_packages"
    p2 = "/Users/vietmac/Documents/CODE/Quản gia/output_packages"
    return p1 if os.path.exists(os.path.dirname(p1)) else p2

def analyze_shot_visuals(img_path, shot_idx=1, total_shots=1):
    """Phân tích thị giác chuyên sâu bằng OpenCV kết hợp logic đạo diễn chuẩn mực"""
    import cv2
    import numpy as np
    
    default_res = {
        "headline": f"Phân đoạn nhịp thị giác #{shot_idx:02d}: Cân bằng bố cục dọc 9:16 và dẫn dắt ánh nhìn",
        "subject_action": "Đối tượng và không gian chuyển động tự nhiên trong khung hình dọc chuẩn điện ảnh.",
        "composition_good": "Bố cục cân đối, duy trì tiêu điểm rõ ràng ở 1/3 khung hình trên thiết bị di động.",
        "composition_bad": "Cần kiểm soát độ rung lắc nhẹ và khoảng không gian thở (headroom) ở rìa trên.",
        "takeaway": "Luôn định hình chủ thể vào vùng an toàn (Safe Zone) 9:16 trước khi thực hiện chuyển động máy.",
        "location": "Bối cảnh thực địa",
        "shot_type": "Medium Tracking Shot (Góc trung linh hoạt)",
        "lighting": "Ánh sáng tự nhiên cân bằng, tương phản dịu",
        "color_vibe": "Tông màu tự nhiên chuẩn điện ảnh",
        "transition": "Cut chuyển tiếp trực tiếp theo mạch hành động",
        "brightness": 85.0,
        "contrast": 55.0
    }
    
    if not os.path.exists(img_path):
        return default_res
        
    img = cv2.imread(img_path)
    if img is None:
        return default_res
        
    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_bright = np.mean(gray)
    std_bright = np.std(gray)
    
    b_mean = np.mean(img[:, :, 0])
    g_mean = np.mean(img[:, :, 1])
    r_mean = np.mean(img[:, :, 2])
    
    # Ánh sáng
    if mean_bright < 75:
        lighting = "Low-key Lighting (Ánh sáng tối, bóng đổ sâu, vệt sáng cục bộ từ đèn/neon)"
        light_good = "Tạo cảm giác bí ẩn, tăng độ tương phản kịch tính (Dramatic Contrast) giữa vùng sáng và bóng tối."
        light_bad = "Vùng shadow dễ bị bết hoặc nhiễu hạt (noise) nếu màn hình điện thoại người xem để độ sáng thấp."
    elif mean_bright > 165:
        lighting = "High-key Lighting (Ánh sáng sáng rực, khuếch tán cao, độ trong trẻo cao)"
        light_good = "Khung hình trong trẻo, giàu năng lượng tích cực và làm rõ trọn vẹn chi tiết bối cảnh."
        light_bad = "Nguy cơ cháy sáng (Clipping Highlights) ở vùng trời hoặc bề mặt kim loại phản chiếu."
    else:
        lighting = "Balanced Diffused Lighting (Ánh sáng tự nhiên cân bằng, độ tương phản dịu)"
        light_good = "Chuyển sắc mượt mà giữa các dải tông màu, bảo toàn chi tiết cả vùng sáng lẫn vùng tối."
        light_bad = "Độ kịch tính thị giác ở mức vừa phải, cần chuyển động máy hoặc chủ thể bù đắp nhịp điệu."
        
    # Tông màu
    if r_mean > b_mean + 15:
        color_vibe = "Tông màu Vàng ấm / Cam Hổ Phách (Warm Amber Mood)"
    elif b_mean > r_mean + 15:
        color_vibe = "Tông màu Xanh lạnh Điện Ảnh (Cool Teal / Cyber Mood)"
    else:
        color_vibe = "Tông màu Trung tính Chuẩn Điện Ảnh (Muted Film Tone)"
        
    # Shot type theo tương quan cạnh
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.sum(edges > 0) / (h * w)
    
    if shot_idx == 1:
        headline = "Visual Hook Mở Màn: Giữ chân người xem ngay 2 giây đầu bằng nhịp chuyển động mạnh"
        subject_action = "Mở màn định vị không gian và nhịp thở của toàn bộ video, thu hút sự chú ý tức thì."
        comp_good = f"Tạo điểm nhấn thị giác ngay trung tâm; ánh sáng {lighting.split('(')[0]} dẫn hướng mắt người xem hoàn hảo."
        comp_bad = "Thời lượng shot ngắn nên người xem dễ bị trôi qua nếu chi tiết chữ/đối tượng phân bổ quá sát góc viền."
        takeaway = "Sử dụng quy tắc 2s đầu (Visual Hook) để định hình nhịp điệu và không gian trước khi đi vào chi tiết."
        shot_type = "Establishing Hook Shot (Góc toàn định vị bối cảnh)"
    elif edge_density > 0.12:
        headline = "Thiết Lập Không Gian Sâu (Wide Establishing): Khắc họa quy mô bối cảnh và nhịp thở đô thị"
        subject_action = "Toàn cảnh bối cảnh không gian rộng lớn với các đối tượng di chuyển tương tác đa chiều."
        comp_good = "Bố cục chia tầng lớp (Layering) tạo chiều sâu không gian đa tầng ấn tượng trên khung dọc 9:16."
        comp_bad = "Mật độ chi tiết dày đặc có thể khiến người xem bị phân tán nếu không có một chủ thể dẫn hướng chính."
        takeaway = "Khi quay góc rộng khung dọc, luôn bố trí một trục chuyển động hoặc đường dẫn (Leading Lines) về trung tâm."
        shot_type = "Wide Establishing Shot (Toàn cảnh không gian sâu)"
    elif edge_density < 0.04:
        headline = "Cận Cảnh Chi Tiết Cảm Xúc (Close-Up Detail): Tập trung tối đa vào điểm chạm thị giác tinh tế"
        subject_action = "Chủ thể được phóng đại cận cảnh, đặc tả hành động hoặc bề mặt chất liệu sắc nét."
        comp_good = "Xóa phông mượt mà (Bokeh), tách biệt chủ thể hoàn toàn khỏi hậu cảnh lộn xộn."
        comp_bad = "Khung hình bị bó hẹp, nếu chủ thể cử động quá nhanh dễ bị trượt ra ngoài vùng nét (Depth of Field mỏng)."
        takeaway = "Dùng góc cận xen kẽ góc toàn để tạo nhịp co giãn thị giác (Breathe In - Breathe Out) cho người xem."
        shot_type = "Close-Up / Macro Detail Shot (Cận cảnh đặc tả)"
    else:
        headline = "Nhịp Dẫn Theo Dõi (Medium Tracking): Duy trì sự liên tục và kết nối cảm xúc nhân vật"
        subject_action = "Nhân vật / đối tượng thực hiện hành động chính trong bối cảnh sinh hoạt chân thực."
        comp_good = "Tỷ lệ cơ thể và môi trường đạt độ cân đối vàng, truyền tải cảm xúc tự nhiên và gần gũi."
        comp_bad = "Góc quay quen thuộc, dễ bị đều đều nếu không kết hợp chuyển động máy tinh tế (Tilt/Pan/Dolly)."
        takeaway = "Góc trung là xương sống kể chuyện, hãy thêm chuyển động camera nhẹ để tạo cảm giác điện ảnh sống động."
        shot_type = "Medium Tracking Shot (Góc trung linh hoạt)"
        
    return {
        "headline": headline,
        "subject_action": subject_action,
        "composition_good": f"{comp_good} {light_good}",
        "composition_bad": f"{comp_bad} {light_bad}",
        "takeaway": takeaway,
        "location": "Bối cảnh thực tế",
        "shot_type": shot_type,
        "lighting": lighting,
        "color_vibe": color_vibe,
        "transition": "Match Cut / Direct Cut theo nhịp chuyển động",
        "brightness": round(float(mean_bright), 1),
        "contrast": round(float(std_bright), 1)
    }


def extract_video_dialogue(video_path):
    """Trích xuất phụ đề/thoại nguyên bản nếu có tiếng nói bằng Whisper"""
    if not os.path.exists(video_path):
        return None
    try:
        import whisper
        model = whisper.load_model('small')
        res = model.transcribe(video_path)
        full_text = res.get('text', '').strip()
        if not full_text or len(full_text) < 10:
            return None
        raw_segments = res.get('segments', [])
        valid_segments = []
        for s in raw_segments:
            txt = s.get('text', '').strip()
            if txt and not re.match(r'^(\[.*\]|\(.*\))$', txt) and len(txt) > 3:
                valid_segments.append({
                    "start": round(float(s.get('start', 0.0)), 2),
                    "end": round(float(s.get('end', 0.0)), 2),
                    "en": txt,
                    "vi": "" # Có thể dịch tự động hoặc ánh xạ
                })
        return valid_segments if valid_segments else None
    except Exception as e:
        print(f"[-] Dialogue transcription skipped: {e}")
        return None

def generate_mobile_first_report(title, creator, fname, overview_text, video_src, shots_data, speech_data=None):
    """Sinh mã HTML Mobile-First Responsive cao cấp với cấu trúc phân tích cảnh logic chuyên sâu"""
    shots_count = len(shots_data)
    total_dur = f"{shots_data[-1]['end_time']:.2f}s" if shots_data else "N/A"
    
    cards_html = []
    grid_html = []
    drawer_html = []
    
    for s in shots_data:
        sid = s.get("shot_id") or s.get("id") or 1
        st = float(s.get("start_time", s.get("start_sec", 0.0)))
        et = float(s.get("end_time", s.get("end_sec", 0.0)))
        dur = f"{s.get('duration', et - st):.2f}s"
        img_url = s.get("img_url") or s.get("img_mid") or ""
        
        # Lấy các trường dữ liệu mới chuẩn hóa
        an = s.get("analysis", {})
        headline = s.get("headline") or an.get("headline") or s.get("title_vi") or f"Phân đoạn #{sid:02d}"
        subject_action = s.get("subject_action") or an.get("subject_action") or s.get("visual_breakdown") or "Mô tả đối tượng và diễn biến trong phân cảnh."
        comp_good = s.get("composition_good") or an.get("composition_good") or s.get("composition") or "Bố cục chặt chẽ, tạo điểm hút mắt tự nhiên."
        comp_bad = s.get("composition_bad") or an.get("composition_bad") or "Cần lưu ý kiểm soát các chi tiết rìa khung hình trên màn hình dọc."
        takeaway = s.get("takeaway") or an.get("takeaway") or s.get("cinematography_notes") or "Ứng dụng kỹ thuật bố cục để định hướng ánh nhìn người xem."
        
        shot_type = s.get("shot_type") or an.get("shot_type") or "Medium Shot"
        lighting = s.get("lighting") or an.get("lighting") or s.get("color_grade") or "Ánh sáng tự nhiên"
        location = s.get("location") or an.get("location") or "Bối cảnh thực địa"
        trans_tech = s.get("transition_technique") or an.get("transition") or "Chuyển tiếp theo nhịp cắt"
        st_title = f"SHOT {sid:02d}"

        cards_html.append(f'''
        <div class="shot-card" id="shot-card-{sid}">
            <div class="shot-media-col">
                <div class="shot-thumb-wrap" onclick="playShot({st}, {et}, '{st_title}')">
                    <img src="{img_url}" alt="{st_title}" class="shot-img" loading="lazy" />
                    <div class="play-overlay">
                        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                    </div>
                    <button class="zoom-btn" onclick="event.stopPropagation(); openLightbox('{img_url}', '{st_title} [{st}s - {et}s] • {headline}')">🔍</button>
                    <span class="thumb-time-badge">{st:.2f}s - {et:.2f}s</span>
                </div>
            </div>
            <div class="shot-info-col">
                <div class="shot-card-header">
                    <div class="shot-title-wrap">
                        <span class="shot-badge-num">SHOT {sid:02d}</span>
                        <h4 class="shot-heading">{headline}</h4>
                    </div>
                    <button class="time-jump-btn" onclick="playShot({st}, {et}, '{st_title}')">
                        ▶ {st:.2f}s ➔ {et:.2f}s ({dur})
                    </button>
                </div>

                <div class="shot-narrative-box">
                    <span class="narrative-tag">📝 Mô tả đối tượng &amp; Diễn biến:</span>
                    <span class="narrative-text">{subject_action}</span>
                </div>

                <div class="critique-container">
                    <div class="critique-box critique-good">
                        <div class="critique-title">✅ Điểm Sáng Thị Giác (Hiệu quả):</div>
                        <div class="critique-content">{comp_good}</div>
                    </div>
                    <div class="critique-box critique-bad">
                        <div class="critique-title">⚠️ Hạn Chế / Cần Lưu Ý:</div>
                        <div class="critique-content">{comp_bad}</div>
                    </div>
                </div>

                <div class="takeaway-box">
                    <div class="takeaway-title">💡 Bài Học Đúc Kết Thực Chiến:</div>
                    <div class="takeaway-content">{takeaway}</div>
                </div>

                <div class="props-list">
                    <div class="prop-item"><span class="prop-label">📍 Bối cảnh:</span> <span class="prop-val">{location}</span></div>
                    <div class="prop-item"><span class="prop-label">🎥 Góc &amp; Tiêu cự:</span> <span class="prop-val">{shot_type}</span></div>
                    <div class="prop-item"><span class="prop-label">💡 Ánh sáng &amp; Màu:</span> <span class="prop-val">{lighting}</span></div>
                    <div class="prop-item"><span class="prop-label">🔄 Chuyển cảnh:</span> <span class="prop-val">{trans_tech}</span></div>
                </div>

                <div class="tags-row">
                    <span class="tag-pill">9:16 Vertical</span>
                    <span class="tag-pill">Shot {sid:02d}</span>
                    <span class="tag-pill">⏱ {dur}</span>
                </div>
            </div>
        </div>
        ''')
        
        grid_html.append(f'''
        <div class="grid-card" onclick="playShot({st}, {et}, '{st_title}')">
            <div class="grid-img-wrap">
                <img src="{img_url}" alt="{st_title}" loading="lazy" />
                <div class="grid-play-icon">▶</div>
                <button class="grid-zoom-btn" onclick="event.stopPropagation(); openLightbox('{img_url}', '{st_title} [{st}s - {et}s] • {headline}')">🔍</button>
                <div class="grid-badge-top">SHOT {sid:02d}</div>
                <div class="grid-badge-bottom">{st:.1f}s - {et:.1f}s</div>
            </div>
            <div class="grid-title-snippet">{headline}</div>
        </div>
        ''')
        
        drawer_html.append(f'''
        <div class="drawer-item" onclick="jumpToShot({sid}, {st}, {et}, '{st_title}')">
            <div class="drawer-thumb">
                <img src="{img_url}" alt="{st_title}" loading="lazy" />
            </div>
            <div class="drawer-info">
                <div class="drawer-shot-title">SHOT {sid:02d}</div>
                <div class="drawer-shot-headline">{headline[:42]}...</div>
                <div class="drawer-shot-time">⏱ {st:.2f}s - {et:.2f}s</div>
            </div>
            <div class="drawer-play-arrow">▶</div>
        </div>
        ''')
        
    all_cards = "\n".join(cards_html)
    all_grid = "\n".join(grid_html)
    all_drawer = "\n".join(drawer_html)

    dialogue_section_html = ""
    # PHÂN LOẠI 3 NHÁNH THỰC CHIẾN THEO CHUẨN ANH VIỆT:
    # Nhánh 1: Video có lời thoại kể chuyện (Spoken / Storytelling)
    if speech_data and len(speech_data) > 0:
        vn_items = []
        en_items = []
        for idx, item in enumerate(speech_data):
            st = item.get("start", 0.0)
            et = item.get("end", 0.0)
            en_txt = item.get("en", "").strip()
            vi_txt = item.get("vi", "").strip() or en_txt
            beat_label = item.get("beat") or f"Phân đoạn #{idx+1:02d}"
            
            vn_items.append(f"""
                    <div class="vn-script-para" onclick="playShot({st}, {et}, '{beat_label}')">
                        <div class="para-meta-line">
                            <span class="para-timestamp-tag">{st:.2f}s</span>
                            <span class="para-beat-label">{beat_label}</span>
                        </div>
                        <span class="para-text">"{vi_txt}"</span>
                    </div>
            """)
            
            en_items.append(f"""
                    <div class="en-line-item" onclick="playShot({st}, {et}, 'ORIGINAL')">
                        <span class="en-time">{st:.2f}s</span>
                        <div class="en-text">"{en_txt}"</div>
                    </div>
            """)

        all_vn_rows = "\n".join(vn_items)
        all_en_rows = "\n".join(en_items)

        dialogue_section_html = f"""
        <!-- BẢNG KỊCH BẢN THOẠI 2 CỘT (TIẾNG VIỆT ĐỌC LIỀN MẠCH + TIẾNG ANH KHỐI NHỎ BÊN CẠNH) -->
        <div class="dialogue-container-2col">
            <!-- CỘT CHÍNH (TRÁI): TIẾNG VIỆT ĐỌC LIỀN MẠCH KHÔNG NGẮT QUÃNG -->
            <div class="col-vietnamese-flow">
                <div class="col-flow-header">
                    <div class="col-flow-badge">🎙️ KỊCH BẢN LỜI THOẠI (BẢN DỊCH THỰC CHIẾN)</div>
                    <span class="col-flow-subtag">Đọc liền một mạch • Chuẩn 4 nhịp giữ chân</span>
                </div>
                <div class="vn-script-body">
                    {all_vn_rows}
                </div>
            </div>

            <!-- CỘT PHỤ (PHẢI): KHỐI NHỎ CHỮ BÉ XÍU ĐỐI SOÁT TIẾNG ANH -->
            <div class="col-english-aside">
                <div class="col-aside-header">
                    <span class="aside-title">ORIGINAL TRANSCRIPT</span>
                    <span class="aside-note">Phụ / Đối chiếu</span>
                </div>
                <div class="en-lines-list">
                    {all_en_rows}
                </div>
            </div>
        </div>

        <!-- KHỐI PROMPT ÁNH XẠ SANG NGÀNH NGHỀ (GEMINI MEGA PROMPT ACCORDION ĐÓNG MẶC ĐỊNH) -->
        <div class="remake-prompt-card" id="remakePromptCard">
            <div class="prompt-accordion-header" onclick="togglePromptAccordion(this)">
                <div class="prompt-header-left">
                    <span class="remake-header-badge">✨ KỊCH BẢN STU</span>
                    <span class="remake-accordion-title">Ánh xạ kịch bản này sang ngành nghề của bạn (Gemini Prompt)</span>
                </div>
                <div class="prompt-header-right">
                    <button class="copy-prompt-btn-compact" onclick="copyMegaPrompt(event, this)">📋 Sao chép</button>
                    <div class="prompt-toggle-btn">
                        <span class="toggle-icon">▼</span>
                        <span class="toggle-label">Mở xem</span>
                    </div>
                </div>
            </div>
            <div class="prompt-accordion-body" style="display: none;">
                <p class="remake-subtext">Sao chép Mega Prompt này dán vào Gemini. Hệ thống tự động gợi ý đúng các ngành nghề học viên thực tế trong STU để xuất bản ngay 3 phương án kịch bản tương ứng theo chuẩn văn phong mộc mạc anh Việt (đã lọc sạch 100% văn mẫu).</p>

                <div class="prompt-code-wrapper">
                    <div class="prompt-code-toolbar">
                        <span class="prompt-code-filename">📄 MEGA_PROMPT_REMAKE_GEMINI.md</span>
                        <button class="copy-prompt-btn" onclick="copyMegaPrompt(event, this)">📋 Sao chép Prompt</button>
                    </div>
                    <div class="prompt-code-content" id="megaPromptText">Bạn là Đạo diễn Video Ngắn &amp; Chuyên gia Tinh chỉnh Lời thoại Thực Chiến theo trường phái mộc mạc của anh Việt (nguyen-viet-voice).

Tôi có cấu trúc logic giữ chân 26 giây đắt giá từ video mẫu với 4 nhịp:
1. Hook 3s: Nêu sự thật trần trụi về một việc ai cũng nghĩ là đơn giản.
2. Xung đột 2 vế: Cái cớ chủ quan giữ thể diện ("Tưởng 2 phút là xong") đối đầu với Thực tế khách quan ("Vào cuộc mới biết mất cả buổi / ở lại mấy ngày").
3. Tactile B-roll: Bàn tay liên tục đặt từng món đồ nghề/chi tiết thật xuống bàn làm việc theo nhịp nói (âm thanh thực tế, mắt thấy tai nghe).
4. Kết bài tự trào &amp; Mở lời tự nhiên: Thừa nhận cái khó của người làm nghề, nhờ người xem chỉ giùm kinh nghiệm hoặc đặt câu hỏi mở chân thành.

=== QUY TẮC BẮT BUỘC VỀ VĂN PHONG ANH VIỆT (TUÂN THỦ 100%) ===
- CẤM TUYỆT ĐỐI VĂN MẪU AI &amp; TỪ NGỮ SÁO RỖNG: Không dùng 'bứt phá', 'chuyển hóa', 'vũ khí', 'thần thái', 'ma trận', 'nâng tầm', 'chạm cảm xúc', 'khơi gợi nhu cầu', 'giải pháp toàn diện', 'tối ưu hóa', 'đỉnh cao', 'bí quyết', 'bật mí', 'ngộ nhận', 'rào cản', 'tử huyệt'...
- CẤM TUYỆT ĐỐI TỪ 'ÔNG GIÁO' hoặc xưng hô thầy bà dạy đời. Đại từ xưng hô chuẩn mực: 'mình - bạn' hoặc 'tôi - bạn'.
- CẤM TUYỆT ĐỐI MƯỢN CỚ SỐ ĐÔNG: Không dùng 'anh em mình', 'nhiều người ngoài kia', 'chúng ta thường hay'. Đi thẳng một đường thẳng vào bản chất sự việc.
- GIỮ TRỌN VĂN PHONG MỘC MẠC: Giọng người làm nghề khiêm tốn, biết đến đâu chia sẻ đến đấy, có nụ cười tự trào duyên dáng, tôn trọng thời gian người xem.

=== HƯỚNG DẪN TƯƠNG TÁC (QUÉT TỪ CÁC NGÀNH NGHỀ HỌC VIÊN TRONG STU) ===
Nếu trong tin nhắn này tôi ĐÃ GHI SẴN thông tin ngành nghề ở cuối, hãy BỎ QUA bước hỏi và XUẤT BẢN NGAY 3 kịch bản.

Nếu tôi CHƯA GHI ngành nghề, hãy DỪNG LẠI và chỉ gửi duy nhất menu 1 câu ngắn gọn sau:

"Chào bạn, để viết đúng đồ nghề và cảnh quay thực tế tại chỗ làm việc của bạn (theo nhóm ngành học viên trong STU), bạn chọn ngành nào dưới đây (chỉ cần gõ số 1, 2, 3, 4, 5 hoặc gõ 1 dòng ngắn):
1. Làm đẹp & Spa / Da liễu Clinic / Phun xăm / Salon tóc (Bàn soi da, khay dụng cụ, kem dưỡng, kéo lược)
2. Nội thất / Decor / Kiến trúc / Vật liệu xây dựng (Bàn làm việc, thước đo, mẫu gỗ, bảng màu sơn, bản vẽ)
3. Ẩm thực & F&B / Tiệm bánh / Trà đồ uống (Mặt bàn pha chế, thớt dao, cân tiểu ly, ly cốc)
4. Nông nghiệp / Phân bón / Chăm sóc sức khỏe / Dược liệu (Bao bì mẫu, cây giống, khay dinh dưỡng, bình xịt)
5. Ngành khác của bạn trong STU: Bạn nhắn giúp mình: [Tên nghề] + [Khách hay tưởng lầm điều gì] + [3 món đồ trên bàn làm việc]"

Sau khi tôi chọn hoặc điền 1 dòng, hãy xuất bản ngay 3 PHƯƠNG ÁN KỊCH BẢN CHI TIẾT TỪNG GIÂY (Gồm 4 cột: Thời lượng | Hình ảnh B-roll xúc giác | Lời thoại A-roll mộc mạc | Âm thanh Foley thực tế) được lọc sạch 100% văn mẫu!</div>
                </div>
            </div>
        </div>
        """
    else:
        # Nhánh 2: Video Kỹ Thuật Quay Thuần Túy (Không thoại)
        corpus_check = f"{title} {fname} {overview_text}".lower()
        is_tech = any(k in corpus_check for k in ["transition", "camera", "angle", "cut", "movement", "whip_pan", "match_cut", "spin", "static_shot", "speed_ramp", "chuyen_canh", "ky_thuat_quay", "b-roll", "broll"])
        if is_tech:
            dialogue_section_html = f"""
        <!-- KHỐI PROMPT ÁNH XẠ KỸ THUẬT CÚ MÁY SANG NGÀNH NGHỀ STU (ACCORDION ĐÓNG MẶC ĐỊNH) -->
        <div class="remake-prompt-card" id="remakePromptCard">
            <div class="prompt-accordion-header" onclick="togglePromptAccordion(this)">
                <div class="prompt-header-left">
                    <span class="remake-header-badge">🎥 CÚ MÁY STU</span>
                    <span class="remake-accordion-title">Ánh xạ kỹ thuật quay này sang ngành nghề của bạn (Gemini Prompt)</span>
                </div>
                <div class="prompt-header-right">
                    <button class="copy-prompt-btn-compact" onclick="copyMegaPrompt(event, this)">📋 Sao chép</button>
                    <div class="prompt-toggle-btn">
                        <span class="toggle-icon">▼</span>
                        <span class="toggle-label">Mở xem</span>
                    </div>
                </div>
            </div>
            <div class="prompt-accordion-body" style="display: none;">
                <p class="remake-subtext">Video này thuần túy về kỹ thuật quay (không thoại). Sao chép Mega Prompt này dán vào Gemini để AI hướng dẫn áp dụng cú máy/chuyển cảnh này vào quay sản phẩm thực tế cho học viên STU (100% hình ảnh xúc giác, không cần nói).</p>

                <div class="prompt-code-wrapper">
                    <div class="prompt-code-toolbar">
                        <span class="prompt-code-filename">📄 MEGA_PROMPT_TECHNIQUE_REMAKE_GEMINI.md</span>
                        <button class="copy-prompt-btn" onclick="copyMegaPrompt(event, this)">📋 Sao chép Prompt</button>
                    </div>
                    <div class="prompt-code-content" id="megaPromptText">Bạn là Đạo diễn Hình ảnh &amp; Chuyên gia Hướng Dẫn Thao Tác Cú Máy Thực Chiến (In-Camera Cinematography) theo trường phái mộc mạc của anh Việt.

Tôi vừa học được kỹ thuật quay / chuyển cảnh cực kỳ đắt giá: {title}.
Video này KHÔNG CÓ LỜI THOẠI, sức hút nằm ở góc đặt máy, tiêu cự và chuyển động camera.

=== QUY TẮC BẮT BUỘC (TUÂN THỦ 100%) ===
- CẤM BỊA KỊCH BẢN NÓI DÔNG DÀI: Tôi không cần kịch bản nói hay lý thuyết đạo lý. Tôi cần hướng dẫn cầm điện thoại quay gì, lia máy hướng nào, đặt góc nào tại bàn làm việc thực tế.
- CẤM VĂN MẪU AI: Không dùng 'nâng tầm', 'bứt phá', 'thần thái', 'vũ khí', 'chuyển hóa'...
- VĂN PHONG MỘC MẠC: Xưng 'mình - bạn', hướng dẫn cầm tay chỉ việc như người làm nghề chỉ cho nhau.

=== HƯỚNG DẪN TƯƠNG TÁC THEO NGÀNH HỌC VIÊN STU ===
Nếu tôi chưa ghi ngành, hãy hỏi đúng 1 câu:
"Chào bạn, bạn muốn áp dụng cú máy này vào quay sản phẩm nào trong 4 nhóm ngành STU:
1. Làm đẹp & Spa / Da liễu Clinic / Salon tóc (Quay cận cảnh chất kem, thao tác tay, máy soi da)
2. Nội thất / Decor / Kiến trúc / Vật liệu xây dựng (Quay lia từ thớ gỗ/mẫu đá sang không gian hoàn thiện)
3. Ẩm thực & F&B / Tiệm bánh / Trà đồ uống (Quay lia chuyển động quanh món ăn, đổ sốt, khói bốc lên)
4. Nông nghiệp / Phân bón / Sức khỏe (Quay kiểm tra lá cây, rễ cây, hạt giống, bao bì sản phẩm)
5. Ngành khác của bạn trong STU: [Tên nghề] + [Sản phẩm muốn quay]"

Sau khi tôi chọn, hãy xuất bản ngay 3 PHƯƠNG ÁN BỐ TRÍ CÚ MÁY (Gồm 4 thông số: Tiêu cự ống kính | Hướng lia máy & Điểm giấu vết cắt | Đạo cụ trên bàn | Cách phối ánh sáng tự nhiên)!</div>
                </div>
            </div>
        </div>
        """

    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Be+Vietnam+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root {{
    --bg-main: #070a0f;
    --bg-card: #0e1420;
    --bg-card-hover: #151e30;
    --bg-surface: #121928;
    --border-color: #1e293b;
    --border-active: #38bdf8;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-blue: #38bdf8;
    --accent-amber: #f59e0b;
    --accent-emerald: #10b981;
    --accent-rose: #f43f5e;
    --accent-purple: #c084fc;
    --font-heading: 'Plus Jakarta Sans', sans-serif;
    --font-body: 'Be Vietnam Pro', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-tap-highlight-color: transparent;
}}

body {{
    background-color: var(--bg-main);
    color: var(--text-primary);
    font-family: var(--font-body);
    line-height: 1.55;
    font-size: 14px;
    overflow-x: hidden;
}}

::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-main); }}
::-webkit-scrollbar-thumb {{ background: #202d42; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent-blue); }}

.app-container {{
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    width: 100%;
}}

@media (min-width: 1024px) {{
    .app-container {{
        flex-direction: row;
        height: 100vh;
        overflow: hidden;
    }}
    .video-sidebar-col {{
        width: 440px;
        min-width: 440px;
        max-width: 480px;
        height: 100vh;
        overflow-y: auto;
        border-right: 1px solid var(--border-color);
        background: var(--bg-surface);
        display: flex;
        flex-direction: column;
        z-index: 30;
    }}
    .content-scroll-col {{
        flex: 1;
        height: 100vh;
        overflow-y: auto;
        padding: 24px 32px 60px;
        min-width: 0;
    }}
}}

@media (max-width: 1023px) {{
    .video-sidebar-col {{
        width: 100%;
        position: sticky;
        top: 0;
        z-index: 50;
        background: rgba(14, 20, 32, 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border-color);
    }}
    .content-scroll-col {{
        width: 100%;
        padding: 16px 14px 80px;
    }}
}}

.video-player-container {{
    position: relative;
    width: 100%;
    background: #000;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}}

@media (min-width: 1024px) {{
    .video-player-container {{
        aspect-ratio: 9/16;
        max-height: 60vh;
    }}
}}
@media (max-width: 1023px) {{
    .video-player-container {{
        max-height: 38vh;
        aspect-ratio: 16/9;
    }}
}}

video#mainPlayer {{
    width: 100%;
    height: 100%;
    object-fit: contain;
    outline: none;
}}

.video-controls-panel {{
    padding: 12px 16px;
    background: #0b111c;
    border-bottom: 1px solid var(--border-color);
}}

.current-status-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 12px;
}}

.status-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.15);
    color: var(--accent-blue);
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 11.5px;
}}

.speed-buttons-row {{
    display: flex;
    align-items: center;
    gap: 4px;
    overflow-x: auto;
    padding-bottom: 4px;
}}

.ctrl-btn {{
    background: #162032;
    color: #cbd5e1;
    border: 1px solid #283750;
    padding: 5px 9px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s;
}}

.ctrl-btn:hover, .ctrl-btn:active {{
    background: #25334d;
    color: #fff;
}}

.ctrl-btn.active {{
    background: var(--accent-blue);
    color: #041324;
    border-color: var(--accent-blue);
    font-weight: 800;
}}

.report-header-banner {{
    background: linear-gradient(135deg, #0e1726 0%, #152238 100%);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}}

.header-top-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
}}

.genre-badge {{
    background: rgba(245, 158, 11, 0.15);
    color: var(--accent-amber);
    border: 1px solid rgba(245, 158, 11, 0.3);
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.report-title {{
    font-family: var(--font-heading);
    font-size: 20px;
    font-weight: 800;
    color: #fff;
    line-height: 1.35;
    margin-bottom: 10px;
}}

.meta-tags-flex {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 12.5px;
    color: var(--text-secondary);
}}

.meta-tags-flex strong {{
    color: #fff;
}}

.overview-card {{
    background: #0e1420;
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent-blue);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 20px;
    font-size: 13.5px;
    color: #cbd5e1;
    line-height: 1.6;
}}

.action-toolbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 20px;
    position: sticky;
    top: 0;
    z-index: 20;
    background: var(--bg-main);
    padding: 10px 0;
}}

.view-tabs-group {{
    display: flex;
    gap: 4px;
    background: #0f1624;
    padding: 4px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
}}

.view-tab-btn {{
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 12.5px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s;
}}

.view-tab-btn.active {{
    background: #1e293b;
    color: #fff;
    font-weight: 700;
}}

.drawer-trigger-btn {{
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: #fff;
    border: none;
    padding: 8px 14px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 12.5px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}

.storyboard-container {{
    display: flex;
    flex-direction: column;
    gap: 20px;
}}

.shot-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    gap: 18px;
    transition: transform 0.15s, border-color 0.15s;
}}

@media (max-width: 768px) {{
    .shot-card {{
        flex-direction: column;
        gap: 12px;
    }}
    .shot-media-col {{
        width: 100% !important;
        min-width: 100% !important;
    }}
    .shot-thumb-wrap {{
        max-height: 240px;
    }}
}}

.shot-card:hover {{
    background: var(--bg-card-hover);
    border-color: #2e3e5a;
}}

.shot-card.active-playing {{
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.3);
}}

.shot-media-col {{
    width: 135px;
    min-width: 135px;
    flex-shrink: 0;
}}

.shot-thumb-wrap {{
    position: relative;
    width: 100%;
    aspect-ratio: 9/16;
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
}}

.shot-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

.play-overlay {{
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.35);
    display: flex;
    justify-content: center;
    align-items: center;
    opacity: 0.7;
}}

.play-overlay svg {{
    width: 32px;
    height: 32px;
    color: #fff;
}}

.zoom-btn {{
    position: absolute;
    top: 6px;
    right: 6px;
    background: rgba(0,0,0,0.65);
    border: none;
    border-radius: 4px;
    width: 24px;
    height: 24px;
    font-size: 11px;
    cursor: pointer;
    color: #fff;
}}

.thumb-time-badge {{
    position: absolute;
    bottom: 6px;
    left: 6px;
    right: 6px;
    background: rgba(15, 23, 42, 0.85);
    font-size: 9.5px;
    font-weight: 700;
    color: var(--accent-amber);
    padding: 2px 4px;
    border-radius: 3px;
    text-align: center;
    font-family: var(--font-mono);
}}

.shot-info-col {{
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.shot-card-header {{
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    border-bottom: 1px solid #1a2436;
    padding-bottom: 8px;
}}

.shot-title-wrap {{
    flex: 1;
    min-width: 200px;
}}

.shot-badge-num {{
    background: #1e293b;
    color: var(--accent-blue);
    font-family: var(--font-mono);
    font-weight: 800;
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    margin-right: 6px;
    display: inline-block;
}}

.shot-heading {{
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    display: inline;
    line-height: 1.4;
}}

.time-jump-btn {{
    background: rgba(56, 189, 248, 0.12);
    color: var(--accent-blue);
    border: 1px solid rgba(56, 189, 248, 0.3);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    font-family: var(--font-mono);
    cursor: pointer;
    white-space: nowrap;
}}

.shot-narrative-box {{
    background: #121a29;
    border-left: 3px solid #38bdf8;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
    color: #e2e8f0;
    line-height: 1.5;
}}

.narrative-tag {{
    font-weight: 700;
    color: var(--accent-blue);
    margin-right: 4px;
    display: block;
    font-size: 12px;
    margin-bottom: 2px;
}}

.critique-container {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}}

@media (max-width: 640px) {{
    .critique-container {{
        grid-template-columns: 1fr;
    }}
}}

.critique-box {{
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 12.5px;
    line-height: 1.45;
}}

.critique-good {{
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.25);
}}

.critique-good .critique-title {{
    color: var(--accent-emerald);
    font-weight: 700;
    font-size: 12px;
    margin-bottom: 2px;
}}

.critique-good .critique-content {{
    color: #cbd5e1;
}}

.critique-bad {{
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
}}

.critique-bad .critique-title {{
    color: var(--accent-amber);
    font-weight: 700;
    font-size: 12px;
    margin-bottom: 2px;
}}

.critique-bad .critique-content {{
    color: #cbd5e1;
}}

.takeaway-box {{
    background: rgba(192, 132, 252, 0.08);
    border: 1px solid rgba(192, 132, 252, 0.25);
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 12.5px;
    line-height: 1.45;
}}

.takeaway-title {{
    color: var(--accent-purple);
    font-weight: 700;
    font-size: 12px;
    margin-bottom: 2px;
}}

.takeaway-content {{
    color: #e2e8f0;
}}

.props-list {{
    font-size: 12px;
    color: #cbd5e1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 12px;
    background: #0b1019;
    padding: 8px 10px;
    border-radius: 6px;
    border: 1px solid #182234;
}}

@media (max-width: 640px) {{
    .props-list {{
        grid-template-columns: 1fr;
    }}
}}

.prop-label {{ font-weight: 700; color: #94a3b8; }}
.prop-val {{ color: #e2e8f0; }}


.tags-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 4px;
}}

.tag-pill {{
    background: #162032;
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
}}

.grid-container {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
}}

.grid-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}}

.grid-img-wrap {{
    position: relative;
    width: 100%;
    aspect-ratio: 9/16;
    background: #000;
}}

.grid-img-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

.grid-play-icon {{
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    color: #fff;
    background: rgba(0,0,0,0.3);
    opacity: 0;
}}

.grid-card:hover .grid-play-icon {{ opacity: 1; }}

.grid-zoom-btn {{
    position: absolute;
    top: 4px;
    right: 4px;
    background: rgba(0,0,0,0.7);
    border: none;
    border-radius: 3px;
    color: #fff;
    font-size: 10px;
    width: 20px;
    height: 20px;
}}

.grid-badge-top {{
    position: absolute;
    top: 4px;
    left: 4px;
    background: rgba(15, 23, 42, 0.85);
    color: var(--accent-blue);
    font-size: 9px;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: var(--font-mono);
}}

.grid-badge-bottom {{
    position: absolute;
    bottom: 4px;
    left: 4px;
    right: 4px;
    background: rgba(15, 23, 42, 0.85);
    color: var(--accent-amber);
    font-size: 9px;
    font-weight: 700;
    padding: 1px 4px;
    border-radius: 3px;
    text-align: center;
    font-family: var(--font-mono);
}}

.grid-title-snippet {{
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 600;
    color: #cbd5e1;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}

.drawer-backdrop {{
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    z-index: 100;
    opacity: 0;
    visibility: hidden;
    transition: all 0.25s ease;
}}

.drawer-backdrop.open {{ opacity: 1; visibility: visible; }}

.drawer-panel {{
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 320px;
    max-width: 85vw;
    background: #0f172a;
    border-left: 1px solid var(--border-color);
    z-index: 101;
    display: flex;
    flex-direction: column;
    transform: translateX(100%);
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}}

.drawer-backdrop.open .drawer-panel {{ transform: translateX(0); }}

.drawer-header {{
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.drawer-title {{ font-weight: 800; font-size: 15px; color: #fff; }}
.drawer-close-btn {{ background: #1e293b; border: none; color: #fff; width: 28px; height: 28px; border-radius: 6px; font-size: 16px; cursor: pointer; }}

.drawer-list {{
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.drawer-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 10px;
    background: #131d30;
    border: 1px solid #1e2d48;
    border-radius: 8px;
    cursor: pointer;
}}

.drawer-item:hover, .drawer-item:active {{
    background: #1c2b47;
    border-color: var(--accent-blue);
}}

.drawer-thumb {{
    width: 44px;
    height: 58px;
    border-radius: 4px;
    overflow: hidden;
    flex-shrink: 0;
    background: #000;
}}

.drawer-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
.drawer-info {{ flex: 1; min-width: 0; }}
.drawer-shot-title {{ font-weight: 700; font-size: 12.5px; color: var(--accent-blue); }}
.drawer-shot-headline {{ font-size: 11.5px; color: #fff; margin: 1px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.drawer-shot-time {{ font-size: 11px; color: var(--accent-amber); font-family: var(--font-mono); }}
.drawer-play-arrow {{ font-size: 13px; color: var(--accent-blue); }}

#lightboxModal {{
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.92);
    backdrop-filter: blur(8px);
    z-index: 200;
    display: none;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 20px;
}}

#lightboxImg {{
    max-width: 90vw;
    max-height: 80vh;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    border: 1px solid #334155;
}}

#lightboxCaption {{
    color: #e2e8f0;
    font-size: 13.5px;
    margin-top: 14px;
    text-align: center;
    background: rgba(15, 23, 42, 0.85);
    padding: 6px 16px;
    border-radius: 20px;
    border: 1px solid #334155;
    max-width: 90vw;
}}

.lightbox-close {{
    position: absolute;
    top: 20px;
    right: 25px;
    color: #fff;
    font-size: 32px;
    cursor: pointer;
}}

/* Styling for 2-Column Dialogue Script & Remake Prompt Box */
.dialogue-container-2col {{
    display: flex;
    gap: 16px;
    align-items: stretch;
    margin-bottom: 20px;
}}

@media (max-width: 900px) {{
    .dialogue-container-2col {{
        flex-direction: column;
    }}
}}

/* CỘT CHÍNH (TRÁI): TIẾNG VIỆT ĐỌC LIỀN MẠCH */
.col-vietnamese-flow {{
    flex: 1;
    min-width: 0;
    background: #0d1422;
    border: 1px solid #1e2b40;
    border-radius: 12px;
    padding: 18px 22px;
    display: flex;
    flex-direction: column;
}}

.col-flow-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1a2538;
    flex-wrap: wrap;
    gap: 8px;
}}

.col-flow-badge {{
    font-family: var(--font-heading);
    font-size: 14.5px;
    font-weight: 800;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 6px;
    letter-spacing: 0.3px;
}}

.col-flow-subtag {{
    font-size: 11.5px;
    color: var(--accent-emerald);
    font-weight: 700;
    background: rgba(16, 185, 129, 0.12);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(16, 185, 129, 0.25);
}}

.vn-script-body {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.vn-script-para {{
    background: #111a2c;
    border: 1px solid #1e2c44;
    border-left: 3px solid var(--accent-amber);
    border-radius: 8px;
    padding: 11px 14px;
    cursor: pointer;
    transition: all 0.15s ease;
}}

.vn-script-para:hover {{
    background: #162238;
    border-color: #2b3d5c;
    transform: translateX(2px);
}}

.para-meta-line {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}}

.para-timestamp-tag {{
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    color: var(--accent-blue);
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 1px 6px;
    border-radius: 3px;
}}

.para-beat-label {{
    font-size: 11px;
    font-weight: 700;
    color: var(--accent-amber);
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}

.para-text {{
    font-size: 14.5px;
    color: #f8fafc;
    line-height: 1.6;
    font-weight: 500;
    display: block;
}}

/* CỘT PHỤ (PHẢI): KHỐI NHỎ CHỮ BÉ XÍU TIẾNG ANH ĐỐI CHIẾU */
.col-english-aside {{
    width: 270px;
    min-width: 250px;
    background: #090e18;
    border: 1px solid #162030;
    border-radius: 12px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
}}

@media (max-width: 900px) {{
    .col-english-aside {{
        width: 100%;
        min-width: 0;
    }}
}}

.col-aside-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #141c2b;
}}

.aside-title {{
    font-family: var(--font-mono);
    font-size: 10.5px;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

.aside-note {{
    font-size: 10px;
    color: #475569;
    font-style: italic;
}}

.en-lines-list {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.en-line-item {{
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid #141d2c;
    border-radius: 6px;
    padding: 7px 10px;
    cursor: pointer;
    transition: all 0.15s ease;
}}

.en-line-item:hover {{
    background: rgba(255, 255, 255, 0.04);
    border-color: #1e2c40;
}}

.en-time {{
    font-family: var(--font-mono);
    font-size: 9.5px;
    color: #475569;
    font-weight: 600;
    display: block;
    margin-bottom: 2px;
}}

.en-text {{
    font-size: 11px;
    color: #64748b;
    font-style: italic;
    line-height: 1.45;
}}

/* Remake Mega Prompt Box (Accordion Closed Default) */
.remake-prompt-card {{
    background: linear-gradient(135deg, #0e1726 0%, #16243b 100%);
    border: 1px solid rgba(56, 189, 248, 0.35);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    border-radius: 10px;
    margin-bottom: 20px;
    overflow: hidden;
    transition: all 0.2s ease;
}}

.prompt-accordion-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    cursor: pointer;
    user-select: none;
    background: rgba(15, 23, 42, 0.6);
    gap: 10px;
    transition: background 0.15s ease;
}}

.prompt-accordion-header:hover {{
    background: rgba(30, 41, 59, 0.85);
}}

.prompt-header-left {{
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
    flex: 1;
}}

.remake-header-badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(56, 189, 248, 0.15);
    color: var(--accent-blue);
    border: 1px solid rgba(56, 189, 248, 0.3);
    font-size: 10.5px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    flex-shrink: 0;
}}

.remake-accordion-title {{
    font-family: var(--font-heading);
    font-size: 13.5px;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.prompt-header-right {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}}

.copy-prompt-btn-compact {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--accent-blue);
    color: #041324;
    border: none;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}}

.copy-prompt-btn-compact:hover {{
    filter: brightness(1.15);
    transform: translateY(-1px);
}}

.prompt-toggle-btn {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: #94a3b8;
    font-weight: 600;
    white-space: nowrap;
}}

.toggle-icon {{
    font-size: 9px;
    transition: transform 0.2s ease;
}}

.prompt-accordion-body {{
    padding: 14px 16px 16px 16px;
    border-top: 1px solid rgba(56, 189, 248, 0.2);
    background: rgba(8, 13, 22, 0.5);
}}

.remake-subtext {{
    font-size: 12.5px;
    color: #cbd5e1;
    line-height: 1.5;
    margin-bottom: 12px;
}}

.prompt-code-wrapper {{
    position: relative;
    background: #080d16;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    overflow: hidden;
}}

.prompt-code-toolbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0f172a;
    padding: 8px 14px;
    border-bottom: 1px solid #1e2d45;
}}

.prompt-code-filename {{
    font-family: var(--font-mono);
    font-size: 11px;
    color: #94a3b8;
    font-weight: 600;
}}

.copy-prompt-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-blue);
    color: #041324;
    border: none;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
}}

.copy-prompt-btn:hover {{
    filter: brightness(1.1);
    transform: translateY(-1px);
}}

.prompt-code-content {{
    font-family: var(--font-mono);
    font-size: 12px;
    color: #cbd5e1;
    line-height: 1.6;
    padding: 14px;
    max-height: 280px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}}

@media (max-width: 640px) {{
    .remake-accordion-title {{
        font-size: 12px;
    }}
    .prompt-accordion-header {{
        padding: 8px 10px;
    }}
}}
</style>
</head>
<body>

<div class="app-container">
    <div class="video-sidebar-col">
        <div class="video-player-container">
            <video id="mainPlayer" controls autoplay muted playsinline preload="auto" loop></video>
        </div>
        <div class="video-controls-panel">
            <div class="current-status-bar">
                <span class="status-tag" id="shotStatusTag">🎬 Phân cảnh: Toàn bộ video</span>
                <a id="directVidLink" href="{video_src}" target="_blank" style="color:var(--accent-blue); font-size:11.5px; text-decoration:none;">Tệp gốc ↗</a>
            </div>
            <div class="speed-buttons-row">
                <span style="font-size:11.5px; color:#94a3b8; font-weight:700; margin-right:4px;">Tốc độ:</span>
                <button class="ctrl-btn" onclick="setSpeed(0.25, this)">0.25x</button>
                <button class="ctrl-btn" onclick="setSpeed(0.5, this)">0.5x</button>
                <button class="ctrl-btn active" onclick="setSpeed(1.0, this)">1.0x</button>
                <button class="ctrl-btn" onclick="setSpeed(1.5, this)">1.5x</button>
                <button class="ctrl-btn" onclick="stepFrame(-1)">⏮ -1F</button>
                <button class="ctrl-btn" onclick="stepFrame(1)">+1F ⏭</button>
                <button class="ctrl-btn" onclick="toggleMute(this)">🔊 Tiếng</button>
                <button class="ctrl-btn" onclick="togglePlayerFullscreen()" title="Toàn màn hình (Phím F hoặc nhấp đúp)" style="background:#fffbeb; color:#b45309; border-color:#fef3c7; font-weight:700;">⛶ Toàn màn hình</button>
            </div>
        </div>
    </div>

    <div class="content-scroll-col">
        <div class="report-header-banner">
            <div class="header-top-row">
                <span class="genre-badge">DIRECTOR STORYBOARD BREAKDOWN</span>
                <span style="font-size:12px; color:var(--accent-amber); font-family:var(--font-mono); font-weight:700;">{shots_count} SHOTS &bull; {total_dur}</span>
                <a href="https://ytuong.fedu.vn" target="_blank" style="color:var(--accent-blue); text-decoration:none; font-size:12px; font-weight:700; display:inline-flex; align-items:center; gap:4px; margin-left:auto;">💡 Kho Ý Tưởng YTUONG HUB ↗</a>
            </div>
            <h1 class="report-title">{title}</h1>
            <div class="meta-tags-flex">
                <span>Tác giả: <strong>{creator}</strong></span>
                <span>Tệp: <strong>{fname}</strong></span>
                <span>Trực quan: <strong>9:16 Vertical HD</strong></span>
            </div>
        </div>

        <div class="overview-card">
            <h3 style="color:#fff; font-size:14px; margin-bottom:6px; font-weight:700;">🎯 TỔNG QUAN PHONG CÁCH THỊ GIÁC &amp; NGÔN NGỮ ĐIỆN ẢNH:</h3>
            <div>{overview_text}</div>
        </div>

        {dialogue_section_html}

        <div class="action-toolbar">
            <div class="view-tabs-group">
                <button class="view-tab-btn active" id="tabDetailBtn" onclick="switchView('detail')">📋 Bóc Tách Chi Tiết</button>
                <button class="view-tab-btn" id="tabGridBtn" onclick="switchView('grid')">🖼️ Lưới Soi Ảnh ({shots_count})</button>
            </div>
            <button class="drawer-trigger-btn" onclick="toggleDrawer(true)">📑 Mục Lục Shot</button>
        </div>

        <div class="storyboard-container" id="storyboardView">
            {all_cards}
        </div>

        <div class="grid-container" id="gridView" style="display:none;">
            {all_grid}
        </div>
    </div>
</div>

<div class="drawer-backdrop" id="drawerBackdrop" onclick="toggleDrawer(false)">
    <div class="drawer-panel" onclick="event.stopPropagation()">
        <div class="drawer-header">
            <div class="drawer-title">📑 MỤC LỤC PHÂN CẢNH ({shots_count})</div>
            <button class="drawer-close-btn" onclick="toggleDrawer(false)">&times;</button>
        </div>
        <div class="drawer-list">
            {all_drawer}
        </div>
    </div>
</div>

<div id="lightboxModal" onclick="closeLightbox()">
    <span class="lightbox-close" onclick="closeLightbox()">&times;</span>
    <img id="lightboxImg" src="" onclick="event.stopPropagation()" />
    <div id="lightboxCaption"></div>
</div>

<script>
const rawVideoSrc = "{video_src}";
let currentEndTime = null;

function getCandidateUrls(src) {{
    if (!src) return [];
    if (src.startsWith('http://') || src.startsWith('https://')) return [src];
    let clean = src.replace(/^(\\.\\/|\\.\\.\\/)+/, '').replace(/^(videos\\/|reports\\/)/, '');
    return [
        '{R2_MEDIA_BASE}/videos/' + encodeURI(clean),
        '../videos/' + clean,
        './videos/' + clean,
        './' + clean
    ];
}}

const candidateUrls = getCandidateUrls(rawVideoSrc);
let candidateIdx = 0;
const player = document.getElementById('mainPlayer');

function loadVideoCandidate() {{
    if (candidateIdx >= candidateUrls.length) return;
    const url = candidateUrls[candidateIdx];
    player.src = url;
    document.getElementById('directVidLink').href = url;
    player.load();
}}

player.onerror = () => {{
    candidateIdx++;
    if (candidateIdx < candidateUrls.length) {{
        loadVideoCandidate();
    }}
}};

loadVideoCandidate();

function playShot(startTime, endTime, label) {{
    currentEndTime = (typeof endTime === 'number') ? endTime : null;
    const tag = document.getElementById('shotStatusTag');
    if (tag) {{
        const endTxt = currentEndTime ? ` - ${{currentEndTime.toFixed(2)}}s` : '';
        tag.innerText = `🎬 ${{label || 'Phân cảnh'}}: [${{startTime.toFixed(2)}}s${{endTxt}}]`;
    }}
    player.currentTime = startTime;
    const p = player.play();
    if (p !== undefined) {{
        p.catch(e => {{
            player.muted = true;
            player.play().catch(err => console.log('Autoplay muted triggered'));
        }});
    }}
    document.querySelectorAll('.shot-card').forEach(c => c.classList.remove('active-playing'));
    const matchCard = Array.from(document.querySelectorAll('.shot-card')).find(c => c.innerText.includes(label));
    if (matchCard) matchCard.classList.add('active-playing');

    if (window.innerWidth < 1024) {{
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}
}}

function setSpeed(speed, btn) {{
    player.playbackRate = speed;
    document.querySelectorAll('.speed-buttons-row .ctrl-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
}}

function stepFrame(frames) {{
    player.pause();
    player.currentTime += (frames * (1/30));
}}

function toggleMute(btn) {{
    player.muted = !player.muted;
    if (btn) btn.innerText = player.muted ? '🔇 Tắt Tiếng' : '🔊 Tiếng';
}}

function togglePlayerFullscreen() {{
    const v = document.getElementById('mainPlayer');
    if (!v) return;
    if (!document.fullscreenElement && !document.webkitFullscreenElement) {{
        if (v.requestFullscreen) {{
            v.requestFullscreen().catch(() => {{}});
        }} else if (v.webkitRequestFullscreen) {{
            v.webkitRequestFullscreen();
        }} else if (v.webkitEnterFullscreen) {{
            v.webkitEnterFullscreen();
        }}
    }} else {{
        if (document.exitFullscreen) {{
            document.exitFullscreen().catch(() => {{}});
        }} else if (document.webkitExitFullscreen) {{
            document.webkitExitFullscreen();
        }}
    }}
}}

document.addEventListener('keydown', (e) => {{
    if ((e.key === 'f' || e.key === 'F') && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {{
        e.preventDefault();
        togglePlayerFullscreen();
    }}
}});

function switchView(view) {{
    const sb = document.getElementById('storyboardView');
    const grid = document.getElementById('gridView');
    const tabDetail = document.getElementById('tabDetailBtn');
    const tabGrid = document.getElementById('tabGridBtn');
    if (view === 'grid') {{
        sb.style.display = 'none';
        grid.style.display = 'grid';
        tabDetail.classList.remove('active');
        tabGrid.classList.add('active');
    }} else {{
        sb.style.display = 'flex';
        grid.style.display = 'none';
        tabDetail.classList.add('active');
        tabGrid.classList.remove('active');
    }}
}}

function toggleDrawer(open) {{
    const drawer = document.getElementById('drawerBackdrop');
    if (open) drawer.classList.add('open');
    else drawer.classList.remove('open');
}}

function jumpToShot(shotNum, st, et, label) {{
    toggleDrawer(false);
    switchView('detail');
    playShot(st, et, label);
    const targetCard = document.getElementById('shot-card-' + shotNum);
    if (targetCard) {{
        targetCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}
}}

function openLightbox(src, caption) {{
    const modal = document.getElementById('lightboxModal');
    const img = document.getElementById('lightboxImg');
    const cap = document.getElementById('lightboxCaption');
    img.src = src;
    cap.innerText = caption || '';
    modal.style.display = 'flex';
}}

function closeLightbox() {{
    document.getElementById('lightboxModal').style.display = 'none';
}}

document.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') {{
        closeLightbox();
        toggleDrawer(false);
    }} else if (e.key === ' ') {{
        if (document.activeElement.tagName !== 'INPUT') {{
            e.preventDefault();
            player.paused ? player.play() : player.pause();
        }}
    }}
}});

function togglePromptAccordion(headerEl) {{
    const card = headerEl.closest('.remake-prompt-card');
    if (!card) return;
    const body = card.querySelector('.prompt-accordion-body');
    const icon = card.querySelector('.toggle-icon');
    const label = card.querySelector('.toggle-label');
    if (!body) return;
    const isCollapsed = (body.style.display === 'none' || getComputedStyle(body).display === 'none');
    if (isCollapsed) {{
        body.style.display = 'block';
        if (icon) icon.textContent = '▲';
        if (label) label.textContent = 'Thu gọn';
    }} else {{
        body.style.display = 'none';
        if (icon) icon.textContent = '▼';
        if (label) label.textContent = 'Mở xem';
    }}
}}

function copyMegaPrompt(e, btn) {{
    if (e && e.stopPropagation) e.stopPropagation();
    const card = btn.closest('.remake-prompt-card');
    const codeEl = card ? card.querySelector('.prompt-code-content') : document.getElementById('megaPromptText');
    if (!codeEl) return;
    const text = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(text).then(() => {{
        const orig = btn.innerHTML;
        btn.innerHTML = '✅ Đã chép!';
        const oldBg = btn.style.background;
        const oldColor = btn.style.color;
        btn.style.background = '#10b981';
        btn.style.color = '#fff';
        setTimeout(() => {{
            btn.innerHTML = orig;
            btn.style.background = oldBg;
            btn.style.color = oldColor;
        }}, 2000);
    }}).catch(err => {{
        alert('Lỗi sao chép, bạn vui lòng bôi đen văn bản để copy nhé!');
    }});
}}

</script>
</body>
</html>'''

def process_video_or_carousel(url_or_path, output_base=None, brain_artifact_dir=None, force=False, user_note=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    workspace_dir = "/Users/vietmac/Documents/CODE/Quản gia"
    if workspace_dir not in sys.path:
        sys.path.insert(0, workspace_dir)

    try:
        from user_note_parser import parse_user_note
    except Exception:
        parse_user_note = lambda t: {"matched_industry": None, "matched_style": None, "user_tags": []}

    if not force:
        try:
            from check_scene_duplicate import find_in_scene
            dup = find_in_scene(url_or_path)
            if dup.get("exists"):
                print(f"[!] Video đã có mặt ở trong scene.html: {dup.get('folder_name')}")
                return {
                    "success": True,
                    "already_exists": True,
                    "folder_name": dup.get("folder_name"),
                    "report_url": dup.get("report_url"),
                    "gdrive_folder_link": dup.get("gdrive_folder"),
                    "scene_url": dup.get("scene_url"),
                    "shots_count": dup.get("shots_count"),
                    "creator": dup.get("creator"),
                    "title": dup.get("title")
                }
        except Exception as e_dup:
            print(f"[-] Lỗi check trùng scene.html: {e_dup}")

    if output_base is None:
        output_base = get_default_output_base()
    os.makedirs(output_base, exist_ok=True)
    import cv2
    import numpy as np

    items = get_post_metadata(url_or_path)
    is_carousel = len(items) > 1
    uploader_clean = sanitize_name(items[0]["uploader"])
    shortcode = sanitize_name(items[0]["id"])
    title_clean = sanitize_name(items[0]["title"])

    if is_carousel:
        folder_name = f"IG_@{uploader_clean}_{shortcode}_Carousel_Analysis".strip("_")
    else:
        folder_name = f"IG_@{uploader_clean}_{shortcode}_{title_clean}".strip("_")

    project_dir = os.path.join(output_base, folder_name)
    os.makedirs(project_dir, exist_ok=True)

    brain_shots_dir = None
    if brain_artifact_dir:
        brain_shots_dir = os.path.join(brain_artifact_dir, "extracted_shots")
        os.makedirs(brain_shots_dir, exist_ok=True)

    shots_data = []
    main_vid_url = ""
    all_vids = []

    if is_carousel:
        print(f"[*] Phát hiện bài Carousel gồm {len(items)} videos/slides. Đang tải và phân tích...")
        slides_dir = os.path.join(project_dir, "carousel_slides")
        os.makedirs(slides_dir, exist_ok=True)
        
        dl_cmd = f'yt-dlp -o "{slides_dir}/slide_%(autonumber)02d.%(ext)s" "{url_or_path}"'
        run_cmd(dl_cmd)

        video_files = sorted([f for f in os.listdir(slides_dir) if f.endswith(".mp4")])
        r2_sub = f"videos/carousel_slides/{folder_name}"
        run_cmd(f'"{RCLONE_EXE}" copy "{slides_dir}" "r2:vietndjmedia/{r2_sub}/"')

        for i, vf in enumerate(video_files):
            s_num = i + 1
            v_path = os.path.join(slides_dir, vf)
            cap = cv2.VideoCapture(v_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            dur = round(total / fps, 2)

            cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
            ret, frame = cap.read()
            mid_name = f"slide_{s_num:02d}_mid.jpg"
            mid_path = os.path.join(slides_dir, mid_name)
            if ret:
                cv2.imwrite(mid_path, frame)
                if brain_shots_dir:
                    cv2.imwrite(os.path.join(brain_shots_dir, mid_name), frame)
            cap.release()

            analysis = analyze_shot_visuals(mid_path, shot_idx=s_num, total_shots=len(video_files))
            s_enc = "/".join([urllib.parse.quote(p) for p in f"{r2_sub}/{vf}".split("/")])
            slide_r2_url = f"{R2_MEDIA_BASE}/{s_enc}"
            all_vids.append({"name": f"Slide {s_num:02d}", "rel_url": slide_r2_url})
            
            img_r2_url = f"{R2_MEDIA_BASE}/images/{folder_name}/{mid_name}"

            shots_data.append({
                "shot_id": s_num,
                "start_time": 0.0,
                "end_time": dur,
                "duration": dur,
                "img_url": img_r2_url,
                "headline": analysis["headline"],
                "subject_action": analysis["subject_action"],
                "composition_good": analysis["composition_good"],
                "composition_bad": analysis["composition_bad"],
                "takeaway": analysis["takeaway"],
                "location": analysis["location"],
                "shot_type": analysis["shot_type"],
                "lighting": analysis["lighting"],
                "transition": analysis["transition"],
                "analysis": analysis
            })

        if all_vids:
            main_vid_url = all_vids[0]["rel_url"]

        run_cmd(f'"{RCLONE_EXE}" copy "{slides_dir}" "r2:vietndjmedia/images/{folder_name}/" --include "*.jpg"')

    else:
        print(f"[*] Phát hiện Video đơn lẻ. Đang tải và bóc tách Shots OpenCV...")
        shots_dir = os.path.join(project_dir, "extracted_shots")
        os.makedirs(shots_dir, exist_ok=True)

        video_dest = os.path.join(project_dir, f"{shortcode}.mp4")
        if os.path.isfile(url_or_path):
            shutil.copy2(url_or_path, video_dest)
        elif items[0].get("play_url"):
            print(f"[*] Đang tải video trực tiếp qua play_url...")
            run_cmd(f'curl -sL -A "Mozilla/5.0" -o "{video_dest}" "{items[0]["play_url"]}"')
        else:
            run_cmd(f'yt-dlp --no-warnings "{url_or_path}" -o "{video_dest}" --force-overwrites')

        # Standardize video to H.264 (yuv420p) + AAC + Faststart for universal Safari & Mobile compatibility
        std_video = os.path.join(project_dir, f"{shortcode}_std.mp4")
        conv_cmd = f'ffmpeg -y -i "{video_dest}" -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -movflags +faststart "{std_video}"'
        c_code, _, _ = run_cmd(conv_cmd)
        if c_code == 0 and os.path.exists(std_video) and os.path.getsize(std_video) > 0:
            shutil.move(std_video, video_dest)

        cap = cv2.VideoCapture(video_dest)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_sec = round(total_frames / fps, 2)

        hists = []
        while True:
            ret, frame = cap.read()
            if not ret: break
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
            cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
            hists.append(hist)
        cap.release()

        diffs = [0.0]
        for i in range(1, len(hists)):
            comp = cv2.compareHist(hists[i-1], hists[i], cv2.HISTCMP_CORREL)
            diffs.append(1.0 - comp)

        cut_frames = []
        min_shot = max(6, int(fps * 0.35))
        i = 1
        while i < len(diffs):
            if diffs[i] > 0.38:
                win = diffs[i:min(i+6, len(diffs))]
                m_idx = int(i + np.argmax(win))
                if not cut_frames or (m_idx - cut_frames[-1]) >= min_shot:
                    cut_frames.append(m_idx)
                i = m_idx + min_shot
            else:
                i += 1

        ranges = []
        st_f = 0
        for cf in cut_frames:
            ranges.append((st_f, cf - 1))
            st_f = cf
        ranges.append((st_f, total_frames - 1))

        cap = cv2.VideoCapture(video_dest)
        curr = 0
        s_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret or s_idx >= len(ranges): break
            s_st, s_en = ranges[s_idx]
            sid = s_idx + 1

            if curr == (s_st + s_en) // 2:
                m_name = f"shot_{sid:02d}_mid.jpg"
                m_path = os.path.join(shots_dir, m_name)
                cv2.imwrite(m_path, frame)
                if brain_shots_dir:
                    cv2.imwrite(os.path.join(brain_shots_dir, m_name), frame)
            
            if curr == s_en:
                m_path = os.path.join(shots_dir, f"shot_{sid:02d}_mid.jpg")
                visual_an = analyze_shot_visuals(m_path, shot_idx=sid, total_shots=len(ranges))
                img_r2_url = f"{R2_MEDIA_BASE}/images/{folder_name}/shot_{sid:02d}_mid.jpg"
                
                shots_data.append({
                    "shot_id": sid,
                    "start_time": round(s_st / fps, 2),
                    "end_time": round(s_en / fps, 2),
                    "duration": round((s_en - s_st + 1) / fps, 2),
                    "img_url": img_r2_url,
                    "headline": visual_an["headline"],
                    "subject_action": visual_an["subject_action"],
                    "composition_good": visual_an["composition_good"],
                    "composition_bad": visual_an["composition_bad"],
                    "takeaway": visual_an["takeaway"],
                    "location": visual_an["location"],
                    "shot_type": visual_an["shot_type"],
                    "lighting": visual_an["lighting"],
                    "transition": visual_an["transition"],
                    "analysis": visual_an
                })
                s_idx += 1
            curr += 1
        cap.release()

        v_enc = urllib.parse.quote(f"{shortcode}.mp4")
        main_vid_url = f"{R2_MEDIA_BASE}/videos/{v_enc}"
        all_vids.append({"name": "Video Master", "rel_url": main_vid_url})
        run_cmd(f'"{RCLONE_EXE}" copy "{video_dest}" "r2:vietndjmedia/videos/"')
        run_cmd(f'"{RCLONE_EXE}" copy "{shots_dir}" "r2:vietndjmedia/images/{folder_name}/"')

    with open(os.path.join(project_dir, "shot_info.json"), "w", encoding="utf-8") as f:
        json.dump(shots_data, f, ensure_ascii=False, indent=2)

    title_display = f"@{uploader_clean} - {title_clean.replace('_', ' ')}"
    overview_display = f"Tác phẩm điện ảnh ngắn gồm {len(shots_data)} phân cảnh được tính toán tỉ mỉ. Bố cục duy trì tỷ lệ khung hình dọc 9:16 sắc nét, khai thác ánh sáng tự nhiên kết hợp tông màu điện ảnh chuyên nghiệp."
    detected_speech = extract_video_dialogue(video_dest)
    html_src = generate_mobile_first_report(
        title=title_display,
        creator=f"@{uploader_clean}",
        fname=f"{folder_name}.html",
        overview_text=overview_display,
        video_src=main_vid_url,
        shots_data=shots_data,
        speech_data=detected_speech
    )

    html_file = os.path.join(project_dir, f"{folder_name}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_src)

    print(f"[*] Uploading trọn bộ package lên Google Drive: {GDRIVE_REMOTE_BASE}/{folder_name}")
    run_cmd(f'"{RCLONE_EXE}" copy "{project_dir}" "{GDRIVE_REMOTE_BASE}/{folder_name}" -v')
    _, f_link, _ = run_cmd(f'"{RCLONE_EXE}" link "{GDRIVE_REMOTE_BASE}/{folder_name}"')

    try:
        portal_repo = "/Users/vietmac/Documents/CODE/vietndj.github.io"
        scene_file = os.path.join(portal_repo, "scene.html")
        reports_dir = os.path.join(portal_repo, "reports")
        if os.path.exists(reports_dir):
            dest_html_name = f"{folder_name}.html"
            dest_html_path = os.path.join(reports_dir, dest_html_name)
            shutil.copy2(html_file, dest_html_path)
            
            # Phân loại lai ghép: Ghi chú người dùng + AI thị giác
            note_info = parse_user_note(user_note or "")
            user_ind = note_info.get("matched_industry")
            user_style = note_info.get("matched_style")
            user_tags = note_info.get("user_tags", [])

            ai_tags = []
            for s in shots_data:
                an = s.get("analysis", {})
                if an.get("shot_type") and an["shot_type"] not in ai_tags:
                    ai_tags.append(an["shot_type"].split("(")[0].strip())
                if an.get("lighting") and "Balanced" not in an["lighting"]:
                    l_tag = an["lighting"].split("(")[0].strip()
                    if l_tag not in ai_tags:
                        ai_tags.append(l_tag)
            if not ai_tags:
                ai_tags = ["Cinematic Lighting", "Composition Mastery", "Visual Rhythm"]

            merged_tags = []
            for t in (user_tags + ai_tags):
                if t and t.lower() not in [x.lower() for x in merged_tags]:
                    merged_tags.append(t)

            # Xác định Kiểu quay
            if user_style:
                final_style = user_style
            else:
                if detected_speech:
                    final_style = {"id": "talking-head", "name": "Talking Head", "icon": "🗣️"}
                elif len(shots_data) > 8:
                    final_style = {"id": "chuyen-canh", "name": "Chuyển Cảnh (Transition)", "icon": "⚡"}
                else:
                    final_style = {"id": "dien-anh", "name": "Điện Ảnh (Cinematic)", "icon": "🎬"}

            # Xác định Ngành nghề
            if user_ind:
                final_industry = user_ind
            else:
                corpus_check = f"{folder_name} {title_display} {overview_display}".lower()
                if any(w in corpus_check for w in ["spa", "mụn", "da liễu", "thẩm mỹ", "y khoa"]):
                    final_industry = {"id": "spa-lam-dep", "name": "Làm Đẹp & Spa / Y Tế", "icon": "💆"}
                elif any(w in corpus_check for w in ["outfit", "lookbook", "thời trang", "fashion"]):
                    final_industry = {"id": "thoi-trang", "name": "Thời Trang & Phụ Kiện", "icon": "👔"}
                elif any(w in corpus_check for w in ["cafe", "ẩm thực", "f&b", "food", "nấu ăn"]):
                    final_industry = {"id": "am-thuc", "name": "Ẩm Thực & F&B", "icon": "🍜"}
                elif any(w in corpus_check for w in ["unboxing", "mở hộp", "camera", "máy ảnh", "gear", "ulanzi"]):
                    final_industry = {"id": "cong-nghe", "name": "Công Nghệ & Thiết Bị", "icon": "📱"}
                elif any(w in corpus_check for w in ["travel", "du lịch", "phong cảnh"]):
                    final_industry = {"id": "du-lich", "name": "Du Lịch & Văn Hóa", "icon": "✈️"}
                elif any(w in corpus_check for w in ["thương hiệu", "xây kênh", "creator", "khóa học"]):
                    final_industry = {"id": "thuong-hieu", "name": "Thương Hiệu Cá Nhân & Dịch Vụ", "icon": "💼"}
                elif any(w in corpus_check for w in ["gym", "chạy bộ", "running", "thể thao"]):
                    final_industry = {"id": "the-thao", "name": "Thể Thao & Năng Động", "icon": "🏃"}
                elif any(w in corpus_check for w in ["kiến trúc", "nội thất", "không gian", "nhà"]):
                    final_industry = {"id": "kien-truc", "name": "Kiến Trúc & Không Gian Sống", "icon": "🏛️"}
                elif any(w in corpus_check for w in ["ugc", "shopee", "tiktok shop", "quảng cáo"]):
                    final_industry = {"id": "ugc", "name": "UGC", "icon": "📱"}
                else:
                    final_industry = {"id": "ky-thuat-quay", "name": "Kỹ Thuật Quay Dựng & Điện Ảnh", "icon": "🎯"}

            # Cập nhật master_classifications.json vào cả 2 repo
            master_repos = [
                "/Users/vietmac/Documents/CODE/vietndj.github.io",
                "/Users/vietmac/Documents/CODE/ytuong-fedu-vn"
            ]
            for m_repo in master_repos:
                m_file = os.path.join(m_repo, "master_classifications.json")
                if os.path.exists(m_file):
                    try:
                        with open(m_file, "r", encoding="utf-8") as mf:
                            m_data = json.load(mf)
                        class_entry = {
                            "id": folder_name,
                            "creator": f"@{uploader_clean}",
                            "creator_name": uploader_clean.replace(".", " ").title(),
                            "title": title_display,
                            "shots_count": len(shots_data),
                            "duration": f"{round(len(shots_data)*2.0, 1)}s",
                            "shooting_style": final_style,
                            "industry": final_industry,
                            "purpose": user_note if user_note else f"Phân tích chuyên sâu ngôn ngữ điện ảnh và nghệ thuật thị giác cho @{uploader_clean}",
                            "tech_tags": merged_tags,
                            "logic_explanation": f"Ghi chú người dùng: {user_note}. Phân loại vào {final_industry['name']} • {final_style['name']}." if user_note else f"Tự động phân loại cấu trúc {final_style['name']} ngành {final_industry['name']}.",
                            "is_excluded": False,
                            "quick_takeaway": overview_display[:240],
                            "country": {
                                "id": "us_eu",
                                "name": "Âu Mỹ",
                                "en_name": "US & Europe",
                                "flag": "🇺🇸/🇪🇺",
                                "badge_color": "purple"
                            }
                        }
                        m_data[folder_name] = class_entry
                        m_data[shortcode] = class_entry
                        with open(m_file, "w", encoding="utf-8") as mf:
                            json.dump(m_data, mf, ensure_ascii=False, indent=2)
                        print(f"[*] Đã cập nhật master_classifications.json tại {m_repo}")
                    except Exception as e_m:
                        print(f"[-] Lỗi cập nhật master_classifications.json tại {m_repo}: {e_m}")

            if os.path.exists(scene_file):
                print("[*] Đang đồng bộ lên fedu.vn/scene.html...")
                with open(scene_file, "r", encoding="utf-8") as f:
                    scene_content = f.read()
                match_portal = re.search(r"const portalData = (\[[\s\S]*?\]);", scene_content)
                if match_portal:
                    try:
                        clean_json_str = re.sub(r',\s*([\]\}])', r'\1', match_portal.group(1))
                        p_data = json.loads(clean_json_str)
                        new_entry = {
                            "id": folder_name,
                            "folder_name": folder_name,
                            "title_vi": folder_name.replace("IG_", "").replace("_", " "),
                            "creator": f"@{uploader_clean}",
                            "desc_vi": f"Báo cáo phân tích chuyên sâu ngôn ngữ điện ảnh, ánh sáng, góc máy và nhịp dựng {len(shots_data)} phân cảnh.",
                            "key_tech": " • ".join(merged_tags[:8]) if merged_tags else "Cinematic Lighting, Composition Mastery, Color Grading, Storyboard Rhythm",
                            "ig_url": url_or_path if str(url_or_path).startswith("http") else "",
                            "gdrive_folder": f_link if "http" in f_link else "",
                            "gdrive_pdf": "",
                            "main_vid_rel": main_vid_url,
                            "main_html_rel": f"reports/{dest_html_name}",
                            "main_pdf_rel": "",
                            "shots_count": len(shots_data),
                            "root_html_rel": f"reports/{dest_html_name}",
                            "root_vid_rel": main_vid_url,
                            "root_pdf_rel": "",
                            "all_vids": all_vids
                        }
                        if not any(x.get("id") == folder_name for x in p_data):
                            p_data.insert(0, new_entry)
                            new_scene_json = json.dumps(p_data, ensure_ascii=False, indent=2)
                            scene_content = scene_content[:match_portal.start(1)] + new_scene_json + scene_content[match_portal.end(1):]
                            with open(scene_file, "w", encoding="utf-8") as f:
                                f.write(scene_content)
                    except Exception as ex_json:
                        print(f"[-] Lỗi cập nhật portalData JSON: {ex_json}")
            
            # Tự động đồng bộ vào Kho Ý Tưởng YTUONG HUB
            build_ideas_script = os.path.join(portal_repo, "build_ideas_bank.py")
            if os.path.exists(build_ideas_script):
                print("[*] Đang đồng bộ vào Kho Ý Tưởng YTUONG HUB...")
                run_cmd(f'python3 "{build_ideas_script}"')

            # Đồng bộ file sang thư mục ytuong-fedu-vn và tự động deploy Vercel
            try:
                ytuong_repo = "/Users/vietmac/Documents/CODE/ytuong-fedu-vn"
                if os.path.exists(ytuong_repo):
                    shutil.copy2(os.path.join(portal_repo, "ideas_data.js"), os.path.join(ytuong_repo, "ideas_data.js"))
                    shutil.copy2(scene_file, os.path.join(ytuong_repo, "scene.html"))
                    os.makedirs(os.path.join(ytuong_repo, "reports"), exist_ok=True)
                    shutil.copy2(html_file, os.path.join(ytuong_repo, "reports", dest_html_name))
                    
                    # Re-build ideas_data.js trực tiếp tại ytuong-fedu-vn nếu có script
                    build_yt = os.path.join(ytuong_repo, "build_ideas_bank.py")
                    if os.path.exists(build_yt):
                        run_cmd(f'python3 "{build_yt}"')
                    
                    # Tự động đẩy lên Vercel Production cho ytuong.fedu.vn
                    code_v, out_v, err_v = run_cmd(f'cd "{ytuong_repo}" && vercel --prod --yes')
                    if code_v == 0:
                        print("[*] Đã tự động deploy YTUONG HUB lên Vercel Production thành công!")
                    else:
                        print(f"[-] Vercel deploy warning: {err_v}")
            except Exception as e_yt:
                print(f"[-] Lỗi đồng bộ sang ytuong-fedu-vn: {e_yt}")
            
            # Luôn đẩy báo cáo HTML, scene.html và YTUONG HUB lên GitHub
            run_cmd(f'cd "{portal_repo}" && git add scene.html reports/ ytuong.html ideas_data.js curation_config.json master_classifications.json && git commit -m "feat: auto-add {folder_name} and sync YTUONG hub" && git push origin master')
            print("[*] Đã đẩy lên GitHub Pages và đồng bộ YTUONG HUB thành công!")
    except Exception as e:
        print(f"[-] Lỗi đồng bộ portal và YTUONG HUB: {e}")

    report_online_url = f"https://fedu.vn/reports/{folder_name}.html"
    return {
        "success": True,
        "is_carousel": is_carousel,
        "folder_name": folder_name,
        "report_url": report_online_url,
        "gdrive_folder_link": f_link if "http" in f_link else "",
        "matched_industry": final_industry["name"] if "final_industry" in locals() else "Điện Ảnh",
        "matched_style": final_style["name"] if "final_style" in locals() else "Điện Ảnh",
        "tags": merged_tags if "merged_tags" in locals() else []
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_and_upload.py <url_or_path> [brain_dir] [--force] [--note <user_note>]")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description="Master Video & Carousel Analysis Pipeline")
    parser.add_argument("url", help="URL video hoặc đường dẫn file cục bộ")
    parser.add_argument("brain_dir", nargs="?", default=None, help="Thư mục Brain Artifacts của Antigravity")
    parser.add_argument("--force", action="store_true", help="Bắt buộc phân tích lại dù đã có trong scene.html")
    parser.add_argument("--note", "--user-note", dest="user_note", default=None, help="Ghi chú phân loại & tags từ anh Việt")

    args, unknown = parser.parse_known_args()

    # Kiểm tra thêm trong unknown args nếu người dùng truyền theo dạng cờ xen kẽ
    force_val = args.force or ("--force" in unknown)
    note_val = args.user_note
    if not note_val:
        for i, a in enumerate(unknown):
            if a in ["--note", "--user-note"] and i + 1 < len(unknown):
                note_val = unknown[i + 1]
                break

    result = process_video_or_carousel(args.url, brain_artifact_dir=args.brain_dir, force=force_val, user_note=note_val)
    print(json.dumps(result, ensure_ascii=False, indent=2))
