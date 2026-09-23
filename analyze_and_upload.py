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
import html
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
R2_MEDIA_BASE = "https://media.fedu.vn"

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

    cmd = f'yt-dlp --cookies-from-browser chrome --no-warnings --dump-json "{url_or_path}"'
    code, out, _ = run_cmd(cmd)
    items = []
    if code == 0 and out:
        lines = [l for l in out.strip().split('\n') if l.strip()]
        for l in lines:
            try:
                data = json.loads(l)
                title = data.get("title", "video")
                desc = data.get("description", "")
                if (title.startswith("Video by") or title == "video") and desc:
                    clean_lines = [cl.strip() for cl in desc.split('\n') if cl.strip() and not cl.strip().startswith('#')]
                    if clean_lines:
                        title = clean_lines[0][:50]
                uploader = data.get("channel") or data.get("uploader_id") or data.get("uploader") or "creator"
                items.append({
                    "id": data.get("id", "video"),
                    "uploader": uploader,
                    "title": title,
                    "description": desc,
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


def _load_report_template():
    """Load report_template.html from same directory as this script."""
    tmpl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_template.html")
    if not os.path.exists(tmpl_path):
        raise FileNotFoundError(f"Template not found: {tmpl_path}")
    with open(tmpl_path, "r", encoding="utf-8") as f:
        return f.read()

def _esc(text):
    """Escape HTML entities in user-provided text."""
    if not text:
        return ""
    return html.escape(str(text), quote=True)

def generate_mobile_first_report(title, creator, fname, overview_text, video_src, shots_data, speech_data=None, custom_headline=None, script_axis=None, industry=None, shooting_style=None, source_url=None, creator_url=None, youtube_url=None):
    """Sinh mã HTML Light Theme chuẩn 30ngayviral cho báo cáo bóc tách video."""
    shots_count = len(shots_data)
    total_dur = f"{shots_data[-1]['end_time']:.2f}s" if shots_data else "N/A"
    
    display_title = custom_headline if custom_headline else title
    
    # Derive URLs from creator name if not provided
    clean_creator = creator.lstrip("@") if creator else "creator"
    if not creator_url:
        creator_url = f"https://www.instagram.com/{clean_creator}/"
    if not source_url:
        # Try to extract shortcode from folder name
        parts = fname.replace(".html", "").split("_") if fname else []
        shortcode = parts[2] if len(parts) > 2 else ""
        source_url = f"https://www.instagram.com/reel/{shortcode}/" if shortcode else creator_url

    # === BADGES ===
    badges_parts = []
    if industry:
        badges_parts.append(f'<span class="badge">{_esc(industry)}</span>')
    if shooting_style:
        badges_parts.append(f'<span class="badge badge-alt">{_esc(shooting_style)}</span>')
    if not badges_parts:
        badges_parts.append('<span class="badge">STORYBOARD BREAKDOWN</span>')
    badges_html = " ".join(badges_parts)

    # === SCRIPT AXIS ===
    script_axis_html = ""
    if script_axis:
        script_axis_html = f"""
        <section class="axis-card">
            <h3 class="axis-title">TRỤC KỊCH BẢN 3 NHỊP</h3>
            <div class="axis-content">{_esc(script_axis)}</div>
        </section>"""

    # === VIDEO PLAYER ===
    if youtube_url:
        # Extract video ID from YouTube URL
        yt_id = ""
        if "youtu.be/" in youtube_url:
            yt_id = youtube_url.split("youtu.be/")[-1].split("?")[0]
        elif "watch?v=" in youtube_url:
            yt_id = youtube_url.split("watch?v=")[-1].split("&")[0]
        elif "/embed/" in youtube_url:
            yt_id = youtube_url.split("/embed/")[-1].split("?")[0]
        video_player_html = f'<iframe id="mainPlayer" src="https://www.youtube.com/embed/{yt_id}?rel=0&modestbranding=1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="width:100%;aspect-ratio:9/16;border-radius:12px;"></iframe>'
    else:
        video_player_html = f'<video id="mainPlayer" src="{_esc(video_src)}" controls autoplay muted playsinline preload="auto" loop style="width:100%;aspect-ratio:9/16;border-radius:12px;background:#000;"></video>'

    # === SHOT CARDS (COMPACT) ===
    cards_html = []
    grid_html = []
    drawer_html = []
    
    for s in shots_data:
        sid = s.get("shot_id") or s.get("id") or 1
        st = float(s.get("start_time", s.get("start_sec", 0.0)))
        et = float(s.get("end_time", s.get("end_sec", 0.0)))
        dur = f"{s.get('duration', et - st):.2f}s"
        img_url = s.get("img_url") or s.get("img_mid") or ""
        
        # Get analysis fields
        an = s.get("analysis", {})
        headline_text = s.get("headline") or an.get("headline") or s.get("title_vi") or f"Phân đoạn #{sid:02d}"
        subject_action = s.get("subject_action") or an.get("subject_action") or ""
        comp_good = s.get("composition_good") or an.get("composition_good") or s.get("composition") or ""
        comp_bad = s.get("composition_bad") or an.get("composition_bad") or ""
        takeaway = s.get("takeaway") or an.get("takeaway") or s.get("cinematography_notes") or ""
        
        shot_type = s.get("shot_type") or an.get("shot_type") or ""
        lighting = s.get("lighting") or an.get("lighting") or s.get("color_grade") or ""
        location = s.get("location") or an.get("location") or ""
        trans_tech = s.get("transition_technique") or an.get("transition") or ""
        
        # Key insight = takeaway (the single most important sentence)
        key_insight = takeaway if takeaway else subject_action
        
        st_title = f"SHOT {sid:02d}"
        
        # COMPACT SHOT CARD
        cards_html.append(f'''
        <div class="shot-card" id="shot-card-{sid}">
            <div class="shot-thumb" onclick="playShot({st}, {et}, '{st_title}')">
                <img src="{img_url}" alt="{st_title}" loading="lazy" />
                <div class="shot-play-icon"><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><polygon points="5 3 19 12 5 21 5 3"/></svg></div>
                <span class="shot-time-badge">{st:.1f}s – {et:.1f}s</span>
            </div>
            <div class="shot-body">
                <div class="shot-head">
                    <span class="shot-num">{st_title}</span>
                    <span class="shot-dur">{dur}</span>
                </div>
                <h4 class="shot-headline">{_esc(headline_text)}</h4>
                <p class="shot-insight">{_esc(key_insight)}</p>
                <details class="shot-details">
                    <summary>Chi tiết kỹ thuật ▸</summary>
                    <div class="shot-meta-grid">
                        {f'<div class="meta-item"><span class="meta-label">Bối cảnh</span><span class="meta-val">{_esc(location)}</span></div>' if location else ''}
                        {f'<div class="meta-item"><span class="meta-label">Góc máy</span><span class="meta-val">{_esc(shot_type)}</span></div>' if shot_type else ''}
                        {f'<div class="meta-item"><span class="meta-label">Ánh sáng</span><span class="meta-val">{_esc(lighting)}</span></div>' if lighting else ''}
                        {f'<div class="meta-item"><span class="meta-label">Chuyển cảnh</span><span class="meta-val">{_esc(trans_tech)}</span></div>' if trans_tech else ''}
                    </div>
                    {f'<div class="critique-good">{_esc(comp_good)}</div>' if comp_good else ''}
                    {f'<div class="critique-warn">{_esc(comp_bad)}</div>' if comp_bad else ''}
                    {f'<div class="shot-narrative">{_esc(subject_action)}</div>' if subject_action and subject_action != key_insight else ''}
                </details>
            </div>
        </div>''')
        
        # GRID ITEM
        grid_html.append(f'''
        <div class="grid-item" onclick="playShot({st}, {et}, '{st_title}')">
            <div class="grid-img-wrap">
                <img src="{img_url}" alt="{st_title}" loading="lazy" />
                <span class="grid-num">{st_title}</span>
                <span class="grid-time">{st:.1f}s – {et:.1f}s</span>
                <button class="grid-zoom" onclick="event.stopPropagation(); openLightbox('{img_url}', '{st_title} • {_esc(headline_text)}')">⊕</button>
            </div>
            <div class="grid-title">{_esc(headline_text[:40])}</div>
        </div>''')
        
        # DRAWER ITEM
        drawer_html.append(f'''
        <div class="drawer-item" onclick="jumpToShot({sid}, {st}, {et}, '{st_title}')">
            <div class="drawer-thumb"><img src="{img_url}" alt="{st_title}" loading="lazy" /></div>
            <div class="drawer-info">
                <div class="drawer-shot-num">{st_title}</div>
                <div class="drawer-shot-hl">{_esc(headline_text[:42])}</div>
                <div class="drawer-shot-time">{st:.2f}s – {et:.2f}s</div>
            </div>
            <div class="drawer-arrow">▶</div>
        </div>''')

    all_cards = "\n".join(cards_html)
    all_grid = "\n".join(grid_html)
    all_drawer = "\n".join(drawer_html)

    # === DIALOGUE SECTION (keep existing logic, restyle for light theme) ===
    dialogue_section_html = ""
    if speech_data and len(speech_data) > 0:
        vn_items = []
        en_items = []
        for idx, item in enumerate(speech_data):
            s_start = item.get("start", 0.0)
            s_end = item.get("end", 0.0)
            en_txt = item.get("en", "").strip()
            vi_txt = item.get("vi", "").strip() or en_txt
            beat_label = item.get("beat") or f"Phân đoạn #{idx+1:02d}"
            
            vn_items.append(f"""
                <div class="vn-para" onclick="playShot({s_start}, {s_end}, '{_esc(beat_label)}')">
                    <span class="vn-time">{s_start:.2f}s</span>
                    <span class="vn-beat">{_esc(beat_label)}</span>
                    <span class="vn-text">"{_esc(vi_txt)}"</span>
                </div>""")
            
            en_items.append(f"""
                <div class="en-line" onclick="playShot({s_start}, {s_end}, 'ORIGINAL')">
                    <span class="en-time">{s_start:.2f}s</span>
                    <span class="en-text">"{_esc(en_txt)}"</span>
                </div>""")

        all_vn = "\n".join(vn_items)
        all_en = "\n".join(en_items)

        dialogue_section_html = f"""
        <section class="dialogue-section">
            <div class="dialogue-col-main">
                <div class="dialogue-header">
                    <span class="dialogue-badge">KỊCH BẢN LỜI THOẠI</span>
                    <span class="dialogue-sub">Bản dịch thực chiến</span>
                </div>
                <div class="dialogue-body">{all_vn}</div>
            </div>
            <div class="dialogue-col-aside">
                <div class="dialogue-aside-header">
                    <span>ORIGINAL TRANSCRIPT</span>
                </div>
                <div class="dialogue-aside-body">{all_en}</div>
            </div>
        </section>"""

        # Add mega prompt accordion for spoken videos
        dialogue_section_html += f"""
        <div class="remake-prompt-card" id="remakePromptCard">
            <div class="prompt-accordion-header" onclick="togglePromptAccordion(this)">
                <div class="prompt-left">
                    <span class="prompt-badge">KỊCH BẢN STU</span>
                    <span class="prompt-title">Ánh xạ kịch bản sang ngành nghề của bạn</span>
                </div>
                <div class="prompt-right">
                    <button class="prompt-copy-btn" onclick="copyMegaPrompt(event, this)">Sao chép</button>
                    <div class="prompt-toggle">
                        <span class="toggle-icon">▼</span>
                        <span class="toggle-label">Mở xem</span>
                    </div>
                </div>
            </div>
            <div class="prompt-accordion-body" style="display: none;">
                <p class="prompt-desc">Sao chép Mega Prompt này dán vào Gemini. Hệ thống tự động gợi ý đúng các ngành nghề học viên thực tế trong STU.</p>
                <div class="prompt-code-wrap">
                    <div class="prompt-code-bar">
                        <span>MEGA_PROMPT_REMAKE_GEMINI.md</span>
                        <button class="prompt-copy-btn" onclick="copyMegaPrompt(event, this)">Sao chép Prompt</button>
                    </div>
                    <div class="prompt-code-content" id="megaPromptText">Bạn là Đạo diễn Video Ngắn &amp; Chuyên gia Tinh chỉnh Lời thoại Thực Chiến theo trường phái mộc mạc của anh Việt (nguyen-viet-voice).

Tôi có cấu trúc logic giữ chân từ video mẫu với 4 nhịp:
1. Hook 3s: Nêu sự thật trần trụi về một việc ai cũng nghĩ là đơn giản.
2. Xung đột 2 vế: Cái cớ chủ quan giữ thể diện đối đầu với Thực tế khách quan.
3. Tactile B-roll: Bàn tay liên tục đặt từng món đồ nghề/chi tiết thật xuống bàn làm việc theo nhịp nói.
4. Kết bài tự trào &amp; Mở lời tự nhiên: Thừa nhận cái khó của người làm nghề.

=== QUY TẮC VĂN PHONG ===
- CẤM VĂN MẪU AI: Không dùng bứt phá, chuyển hóa, vũ khí, thần thái, nâng tầm...
- CẤM từ ÔNG GIÁO. Xưng hô: mình - bạn hoặc tôi - bạn.
- GIỮ VĂN PHONG MỘC MẠC.

=== HƯỚNG DẪN ===
Nếu tôi chưa ghi ngành nghề, hỏi 1 câu:
1. Làm đẹp &amp; Spa / Da liễu / Salon tóc
2. Nội thất / Decor / Kiến trúc
3. Ẩm thực &amp; F&amp;B / Tiệm bánh
4. Nông nghiệp / Phân bón / Sức khỏe
5. Ngành khác: [Tên nghề] + [3 món đồ trên bàn]

Sau khi chọn → xuất 3 PHƯƠNG ÁN KỊCH BẢN (Thời lượng | B-roll | Lời thoại | Âm thanh Foley)!</div>
                </div>
            </div>
        </div>"""
    else:
        # Check for tech video
        corpus_check = f"{title} {fname} {overview_text}".lower()
        is_tech = any(k in corpus_check for k in ["transition", "camera", "angle", "cut", "movement", "whip_pan", "match_cut", "spin", "static_shot", "speed_ramp", "chuyen_canh", "ky_thuat_quay", "b-roll", "broll"])
        if is_tech:
            dialogue_section_html = f"""
        <div class="remake-prompt-card" id="remakePromptCard">
            <div class="prompt-accordion-header" onclick="togglePromptAccordion(this)">
                <div class="prompt-left">
                    <span class="prompt-badge">CÚ MÁY STU</span>
                    <span class="prompt-title">Ánh xạ kỹ thuật quay sang ngành nghề của bạn</span>
                </div>
                <div class="prompt-right">
                    <button class="prompt-copy-btn" onclick="copyMegaPrompt(event, this)">Sao chép</button>
                    <div class="prompt-toggle">
                        <span class="toggle-icon">▼</span>
                        <span class="toggle-label">Mở xem</span>
                    </div>
                </div>
            </div>
            <div class="prompt-accordion-body" style="display: none;">
                <p class="prompt-desc">Video kỹ thuật quay thuần túy (không thoại). Sao chép Prompt để AI hướng dẫn áp dụng cú máy vào quay sản phẩm thực tế.</p>
                <div class="prompt-code-wrap">
                    <div class="prompt-code-bar">
                        <span>MEGA_PROMPT_TECHNIQUE_REMAKE_GEMINI.md</span>
                        <button class="prompt-copy-btn" onclick="copyMegaPrompt(event, this)">Sao chép Prompt</button>
                    </div>
                    <div class="prompt-code-content" id="megaPromptText">Bạn là Đạo diễn Hình ảnh &amp; Chuyên gia Hướng Dẫn Thao Tác Cú Máy Thực Chiến.

Tôi vừa học được kỹ thuật quay đắt giá: {_esc(title)}.
Video này KHÔNG CÓ LỜI THOẠI, sức hút nằm ở góc đặt máy, tiêu cự và chuyển động camera.

=== QUY TẮC ===
- CẤM BỊA KỊCH BẢN NÓI. Tôi cần hướng dẫn cầm điện thoại quay gì, lia máy hướng nào.
- CẤM VĂN MẪU AI.
- VĂN PHONG MỘC MẠC: Xưng mình - bạn.

=== HƯỚNG DẪN ===
Nếu tôi chưa ghi ngành, hỏi 1 câu:
1. Làm đẹp &amp; Spa (quay kem, thao tác tay, máy soi da)
2. Nội thất / Decor (quay lia thớ gỗ/mẫu đá sang không gian)
3. Ẩm thực &amp; F&amp;B (quay lia quanh món ăn, đổ sốt, khói)
4. Nông nghiệp / Sức khỏe (kiểm tra lá cây, hạt giống, bao bì)
5. Ngành khác: [Tên nghề] + [Sản phẩm muốn quay]

Sau khi chọn → xuất 3 PHƯƠNG ÁN BỐ TRÍ CÚ MÁY!</div>
                </div>
            </div>
        </div>"""

    # === LOAD AND POPULATE TEMPLATE ===
    try:
        tmpl = _load_report_template()
    except FileNotFoundError:
        # Fallback: return minimal HTML if template not found
        return f"<html><body><h1>{_esc(display_title)}</h1><p>Template file not found.</p></body></html>"
    
    replacements = {
        "%%PAGE_TITLE%%": _esc(display_title),
        "%%DISPLAY_TITLE%%": _esc(display_title),
        "%%SOURCE_URL%%": _esc(source_url),
        "%%CREATOR%%": _esc(creator),
        "%%CREATOR_URL%%": _esc(creator_url),
        "%%SHOTS_COUNT%%": str(shots_count),
        "%%TOTAL_DUR%%": total_dur,
        "%%BADGES_HTML%%": badges_html,
        "%%SCRIPT_AXIS_HTML%%": script_axis_html,
        "%%OVERVIEW_TEXT%%": _esc(overview_text),
        "%%VIDEO_PLAYER_HTML%%": video_player_html,
        "%%RAW_VIDEO_SRC%%": _esc(video_src),
        "%%DIALOGUE_HTML%%": dialogue_section_html,
        "%%ALL_CARDS%%": all_cards,
        "%%ALL_GRID%%": all_grid,
        "%%ALL_DRAWER%%": all_drawer,
    }
    
    result = tmpl
    for key, val in replacements.items():
        result = result.replace(key, val)
    
    return result


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
        
        dl_cmd = f'yt-dlp --cookies-from-browser chrome -o "{slides_dir}/slide_%(autonumber)02d.%(ext)s" "{url_or_path}"'
        run_cmd(dl_cmd)

        video_files = sorted([f for f in os.listdir(slides_dir) if f.endswith(".mp4")])
        r2_sub = f"videos/carousel_slides/{folder_name}"
        run_cmd(f'"{RCLONE_EXE}" copy "{slides_dir}" "gdrive:Work/AI_Video_Analysis/{r2_sub}/"')

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
                webp_name = f"slide_{s_num:02d}_mid.webp"
                cv2.imwrite(os.path.join(slides_dir, webp_name), frame)
                if brain_shots_dir:
                    cv2.imwrite(os.path.join(brain_shots_dir, mid_name), frame)
                    cv2.imwrite(os.path.join(brain_shots_dir, webp_name), frame)
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

        run_cmd(f'"{RCLONE_EXE}" copy "{slides_dir}" "gdrive:Work/AI_Video_Analysis/images/{folder_name}/" --include "*.jpg" --include "*.webp"')
        run_cmd(f'"{RCLONE_EXE}" copy "{slides_dir}" "r2:vietndjmedia/images/{folder_name}/" --include "*.jpg" --include "*.webp"')
        run_cmd(f'"{RCLONE_EXE}" copy "{slides_dir}" "r2:vietndjmedia/{r2_sub}/" --include "*.mp4"')

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
            run_cmd(f'yt-dlp --cookies-from-browser chrome --no-warnings "{url_or_path}" -o "{video_dest}" --force-overwrites')

        if not os.path.exists(video_dest) or os.path.getsize(video_dest) == 0:
            for tf in os.listdir("/tmp"):
                if shortcode in tf and tf.endswith(".mp4"):
                    shutil.copy2(os.path.join("/tmp", tf), video_dest)
                    print(f"[*] Đã tận dụng tệp video tải sẵn từ /tmp: {tf}")
                    break

        if not os.path.exists(video_dest) or os.path.getsize(video_dest) == 0:
            raise RuntimeError(f"[-] Không thể tải hoặc mở video: {url_or_path}")

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
                w_name = f"shot_{sid:02d}_mid.webp"
                cv2.imwrite(os.path.join(shots_dir, w_name), frame)
                if brain_shots_dir:
                    cv2.imwrite(os.path.join(brain_shots_dir, m_name), frame)
                    cv2.imwrite(os.path.join(brain_shots_dir, w_name), frame)
            
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
        run_cmd(f'"{RCLONE_EXE}" copy "{video_dest}" "gdrive:Work/AI_Video_Analysis/videos/"')
        run_cmd(f'"{RCLONE_EXE}" copy "{shots_dir}" "gdrive:Work/AI_Video_Analysis/images/{folder_name}/"')
        run_cmd(f'"{RCLONE_EXE}" copy "{shots_dir}" "r2:vietndjmedia/images/{folder_name}/"')
        run_cmd(f'"{RCLONE_EXE}" copy "{video_dest}" "r2:vietndjmedia/videos/"')

    with open(os.path.join(project_dir, "shot_info.json"), "w", encoding="utf-8") as f:
        json.dump(shots_data, f, ensure_ascii=False, indent=2)

    title_display = f"@{uploader_clean} - {title_clean.replace('_', ' ')}"
    # Trích xuất điểm sáng thực chiến then chốt, loại bỏ hoàn toàn văn mẫu máy móc
    hook_takeaway = ""
    if shots_data and len(shots_data) > 0:
        first_shot = shots_data[0]
        hook_takeaway = first_shot.get("takeaway") or first_shot.get("headline") or first_shot.get("subject_action") or ""
    key_takeaway = ""
    if shots_data and len(shots_data) > 1:
        second_shot = shots_data[1]
        key_takeaway = second_shot.get("takeaway") or second_shot.get("headline") or second_shot.get("subject_action") or ""

    if user_note and not any(k in user_note for k in ["Instagram Liked", "Video,", "by @", "shared", "Shared", "of 18"]):
        overview_display = user_note
    elif hook_takeaway and key_takeaway and hook_takeaway != key_takeaway:
        overview_display = f"⚡ {hook_takeaway} ➔ {key_takeaway}"
    elif hook_takeaway:
        overview_display = f"⚡ {hook_takeaway}"
    if is_carousel:
        first_slide_vid = os.path.join(slides_dir, video_files[0]) if video_files else ""
        detected_speech = extract_video_dialogue(first_slide_vid) if first_slide_vid else {"has_speech": False, "transcription": "", "segments": []}
    else:
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

            # Đồng bộ file sang thư mục ytuong-fedu-vn và tự động deploy qua Cloudflare Pages (GitHub)
            try:
                ytuong_repo = "/Users/vietmac/Documents/CODE/ytuong-fedu-vn"
                if os.path.exists(ytuong_repo):
                    shutil.copy2(os.path.join(portal_repo, "ideas_data.js"), os.path.join(ytuong_repo, "ideas_data.js"))
                    shutil.copy2(scene_file, os.path.join(ytuong_repo, "scene.html"))
                    os.makedirs(os.path.join(ytuong_repo, "reports"), exist_ok=True)
                    shutil.copy2(html_file, os.path.join(ytuong_repo, "reports", dest_html_name))
                    
                    # Cập nhật master classifications & curation config (bảo toàn cấu hình tinh chỉnh tại ytuong-fedu-vn)
                    ytuong_m = os.path.join(ytuong_repo, "master_classifications.json")
                    portal_m = os.path.join(portal_repo, "master_classifications.json")
                    if os.path.exists(portal_m):
                        try:
                            with open(portal_m, "r", encoding="utf-8") as pmf:
                                p_data = json.load(pmf)
                            y_data = {}
                            if os.path.exists(ytuong_m):
                                with open(ytuong_m, "r", encoding="utf-8") as ymf:
                                    y_data = json.load(ymf)
                            # Giữ lại các trường fedu_optimization và title_vi tinh chỉnh từ ytuong_repo
                            for k, v in p_data.items():
                                if k not in y_data:
                                    y_data[k] = v
                                else:
                                    # Cập nhật thông tin mới nhất nhưng giữ nguyên fedu_optimization
                                    if "fedu_optimization" in y_data[k] and "fedu_optimization" not in v:
                                        v["fedu_optimization"] = y_data[k]["fedu_optimization"]
                                    if y_data[k].get("title") and not y_data[k].get("title", "").startswith("@"):
                                        v["title"] = y_data[k]["title"]
                                    y_data[k] = v
                            with open(ytuong_m, "w", encoding="utf-8") as ymf:
                                json.dump(y_data, ymf, ensure_ascii=False, indent=2)
                        except Exception as e_m_sync:
                            print(f"[-] Warning sync master_classifications: {e_m_sync}")

                    # Bảo toàn curation_config.json từ ytuong-fedu-vn sang portal_repo
                    yt_curation = os.path.join(ytuong_repo, "curation_config.json")
                    if os.path.exists(yt_curation):
                        shutil.copy2(yt_curation, os.path.join(portal_repo, "curation_config.json"))

                    # Re-build ideas_data.js trực tiếp tại ytuong-fedu-vn nếu có script
                    build_yt = os.path.join(ytuong_repo, "build_ideas_bank.py")
                    if os.path.exists(build_yt):
                        run_cmd(f'python3 "{build_yt}"')
                    
                    # Đẩy code lên GitHub để Cloudflare Pages tự động Deploy
                    code_v, out_v, err_v = run_cmd(f'cd "{ytuong_repo}" && git add . && git commit -m "feat: auto-sync {folder_name}" ; git push origin main')
                    if code_v == 0:
                        print("[*] Đã đẩy YTUONG HUB lên GitHub (Cloudflare Pages sẽ tự động build)!")
                    else:
                        print(f"[-] YTUONG HUB push warning: {err_v}")
            except Exception as e_yt:
                print(f"[-] Lỗi đồng bộ sang ytuong-fedu-vn: {e_yt}")
            
            # Luôn đẩy báo cáo HTML, scene.html và YTUONG HUB lên GitHub (vietndj.github.io)
            code_p, out_p, err_p = run_cmd(f'cd "{portal_repo}" && git add scene.html reports/ ytuong.html ideas_data.js curation_config.json master_classifications.json && git commit -m "feat: auto-add {folder_name} and sync YTUONG hub" ; git push origin master')
            if code_p == 0:
                print("[*] Đã đẩy lên GitHub Pages và đồng bộ YTUONG HUB thành công!")
            else:
                print(f"[-] GitHub Pages push warning: {err_p}")
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
