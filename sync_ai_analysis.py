#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync AI Vision Analysis to HTML Reports & YTUONG HUB
Đồng bộ ngược 100% phân tích thị giác thật của AI vào:
1. shot_info.json
2. File HTML báo cáo cục bộ và trên các repo (vietndj.github.io, ytuong-fedu-vn)
3. master_classifications.json (Phân loại ngành, kiểu quay, tags, overview chuẩn)
4. Rebuild YTUONG ideas bank và git push tự động
"""
import os
import sys
import json
import shutil
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
try:
    from analyze_and_upload import generate_mobile_first_report, sanitize_name
except ImportError:
    pass

PORTAL_REPO = "/Users/vietmac/Documents/CODE/vietndj.github.io"
YTUONG_REPO = "/Users/vietmac/Documents/CODE/ytuong-fedu-vn"
DEFAULT_OUTPUT_BASE = "/Users/vietmac/Documents/CODE/Quản gia/output_packages"

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def sync_analysis(folder_name_or_path, shots_update_file=None, industry=None, style=None, tags=None, overview=None, purpose=None, custom_headline=None, script_axis=None, youtube_url=None):
    if os.path.isdir(folder_name_or_path):
        package_dir = folder_name_or_path
        folder_name = os.path.basename(folder_name_or_path.rstrip("/\\"))
    else:
        folder_name = folder_name_or_path
        package_dir = os.path.join(DEFAULT_OUTPUT_BASE, folder_name)
        if not os.path.exists(package_dir):
            alt_base = "/Users/vietmac/Documents/CODE/Video phan tich/output_packages"
            if os.path.exists(os.path.join(alt_base, folder_name)):
                package_dir = os.path.join(alt_base, folder_name)

    if not os.path.exists(package_dir):
        print(f"[-] Không tìm thấy thư mục package: {package_dir}")
        return False

    shot_info_path = os.path.join(package_dir, "shot_info.json")
    if not os.path.exists(shot_info_path):
        print(f"[-] Không tìm thấy shot_info.json: {shot_info_path}")
        return False

    with open(shot_info_path, "r", encoding="utf-8") as f:
        shots_data = json.load(f)

    # Cập nhật shots_data nếu có file cập nhật
    if shots_update_file and os.path.exists(shots_update_file):
        with open(shots_update_file, "r", encoding="utf-8") as uf:
            updates = json.load(uf)
        for i, s in enumerate(shots_data):
            if i < len(updates):
                up = updates[i]
                for key in ["headline", "subject_action", "composition_good", "composition_bad", "takeaway", "shot_type", "lighting", "transition"]:
                    if key in up:
                        s[key] = up[key]
                        if "analysis" in s:
                            s["analysis"][key] = up[key]
        with open(shot_info_path, "w", encoding="utf-8") as f:
            json.dump(shots_data, f, ensure_ascii=False, indent=2)
        print(f"[+] Đã cập nhật {len(updates)} shots vào {shot_info_path}")

    # Lấy thông tin metadata
    shortcode = folder_name.split("_")[2] if len(folder_name.split("_")) > 2 else "video"
    uploader = folder_name.split("_")[1].lstrip("@") if len(folder_name.split("_")) > 1 else "creator"
    title_raw = "_".join(folder_name.split("_")[3:]) if len(folder_name.split("_")) > 3 else folder_name
    title_display = f"@{uploader} - {title_raw.replace('_', ' ')}"
    main_vid_url = f"https://media.fedu.vn/videos/{shortcode}.mp4"
    
    # Derive URLs
    source_url = f"https://www.instagram.com/reel/{shortcode}/" if shortcode != "video" else ""
    creator_url = f"https://www.instagram.com/{uploader}/"

    # Tự động tìm kiếm hoặc upload YouTube nếu chưa có youtube_url
    if not youtube_url:
        for r in [YTUONG_REPO, PORTAL_REPO]:
            cfg_path = os.path.join(r, "master_classifications.json")
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfgs = json.load(f)
                    for k in [shortcode, folder_name]:
                        if k in cfgs and cfgs[k].get("youtube_url"):
                            youtube_url = cfgs[k].get("youtube_url")
                            break
                except Exception:
                    pass
            if youtube_url:
                break

    if not youtube_url:
        # Tự động tìm file video và upload lên YouTube kênh Sabakiz
        vid_candidates = [
            os.path.join(package_dir, f"{shortcode}.mp4"),
            os.path.join(package_dir, "master.mp4")
        ]
        chosen_vid = None
        for c in vid_candidates:
            if os.path.exists(c):
                chosen_vid = c
                break
        if not chosen_vid:
            for f in os.listdir(package_dir):
                if f.endswith(".mp4") and not f.startswith("slide_"):
                    chosen_vid = os.path.join(package_dir, f)
                    break
        if chosen_vid and os.path.exists(chosen_vid):
            try:
                sys.path.append("/Users/vietmac/Documents/CODE/AI Course/.agents/skills/analyze-video-02/scripts")
                from extract_storyboard_02 import upload_youtube_pipeline
                meta = {
                    "title": title_raw.replace('_', ' '),
                    "uploader": uploader,
                    "webpage_url": source_url,
                    "duration_seconds": 60,
                    "aspect_ratio": "9:16"
                }
                print(f"[*] Đang tự động upload lên YouTube Sabakiz: {chosen_vid}...")
                yt_res = upload_youtube_pipeline(chosen_vid, meta)
                if yt_res and yt_res.get("watch_url"):
                    youtube_url = yt_res.get("short_url") or yt_res.get("watch_url")
                    print(f"[+] Đã upload YouTube thành công: {youtube_url}")
            except Exception as e:
                print(f"[-] Không thể upload YouTube tự động: {e}")

    # Xử lý overview
    if not overview:
        if shots_data and len(shots_data) > 0:
            h1 = shots_data[0].get("headline", "")
            h2 = shots_data[-1].get("headline", "") if len(shots_data) > 1 else ""
            overview = f"⚡ {h1} ➔ {h2}" if h2 else f"⚡ {h1}"
        else:
            overview = f"Phân tích thị giác chi tiết {len(shots_data)} phân cảnh chuẩn điện ảnh."

    # Render lại báo cáo HTML
    html_src = generate_mobile_first_report(
        title=title_display,
        creator=f"@{uploader}",
        fname=f"{folder_name}.html",
        overview_text=overview,
        video_src=main_vid_url,
        shots_data=shots_data,
        speech_data=None,
        custom_headline=custom_headline,
        script_axis=script_axis,
        industry=industry,
        shooting_style=style,
        source_url=source_url,
        creator_url=creator_url,
        youtube_url=youtube_url
    )

    # Ghi file HTML cục bộ
    local_html = os.path.join(package_dir, f"{folder_name}.html")
    with open(local_html, "w", encoding="utf-8") as f:
        f.write(html_src)
    print(f"[+] Đã tạo lại báo cáo HTML: {local_html}")

    # Đồng bộ sang các repo
    shutil.copy2(local_html, os.path.join(PORTAL_REPO, "reports", f"{folder_name}.html"))
    shutil.copy2(local_html, os.path.join(YTUONG_REPO, "reports", f"{folder_name}.html"))
    if os.path.exists(os.path.join(YTUONG_REPO, "dist", "reports")):
        shutil.copy2(local_html, os.path.join(YTUONG_REPO, "dist", "reports", f"{folder_name}.html"))
    print("[+] Đã copy HTML sang vietndj.github.io và ytuong-fedu-vn")

    # Cập nhật master_classifications.json
    for r in [PORTAL_REPO, YTUONG_REPO]:
        cfg_path = os.path.join(r, "master_classifications.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfgs = json.load(f)
            target_keys = [k for k in [shortcode, folder_name] if k in cfgs]
            for target_key in target_keys:
                entry = cfgs[target_key]
                if industry:
                    if isinstance(industry, dict):
                        entry["industry"] = industry
                    else:
                        entry["industry"] = {"id": industry, "name": industry, "icon": "🎯"}
                if style:
                    if isinstance(style, dict):
                        entry["shooting_style"] = style
                    else:
                        entry["shooting_style"] = {"id": style, "name": style, "icon": "🎬"}
                if tags:
                    entry["tech_tags"] = tags if isinstance(tags, list) else [t.strip() for t in tags.split(",")]
                if overview:
                    entry["quick_takeaway"] = overview
                if purpose:
                    entry["purpose"] = purpose
                if youtube_url:
                    yt_id = None
                    if "youtu.be/" in youtube_url:
                        yt_id = youtube_url.split("youtu.be/")[-1].split("?")[0]
                    elif "watch?v=" in youtube_url:
                        yt_id = youtube_url.split("watch?v=")[-1].split("&")[0]
                    elif "/embed/" in youtube_url:
                        yt_id = youtube_url.split("/embed/")[-1].split("?")[0]
                    if yt_id:
                        entry["youtube_id"] = yt_id
                        entry["youtube_url"] = f"https://youtu.be/{yt_id}"
                        entry["youtube_embed"] = f"https://www.youtube.com/embed/{yt_id}"
            if target_keys:
                with open(cfg_path, "w", encoding="utf-8") as f:
                    json.dump(cfgs, f, ensure_ascii=False, indent=2)
                print(f"[+] Đã cập nhật master_classifications.json tại {r}")

    # Rebuild ý tưởng hub
    run_cmd(f'python3 "{YTUONG_REPO}/build_ideas_bank.py"')
    print("[+] Đã build lại ideas_bank trên YTUONG HUB")

    # Deploy Cloudflare Pages
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not cf_token:
        cf_cred_file = os.path.expanduser("~/.gemini/config/cloudflare_credentials.json")
        if os.path.exists(cf_cred_file):
            try:
                with open(cf_cred_file, "r", encoding="utf-8") as cff:
                    cf_data = json.load(cff)
                    cf_token = cf_data.get("api_token")
            except Exception:
                pass
    token_env = f'CLOUDFLARE_API_TOKEN="{cf_token}" ' if cf_token else ""
    deploy_code, deploy_out, deploy_err = run_cmd(
        f'cd "{YTUONG_REPO}" && {token_env}npx wrangler pages deploy dist --project-name ytuong-fedu-vn-pages'
    )
    if deploy_code == 0:
        print("[+] Đã deploy thành công lên Cloudflare Pages (ytuong.fedu.vn)!")
    else:
        print(f"[-] Deploy Cloudflare Pages cảnh báo/lỗi: {deploy_err or deploy_out}")

    # Auto push
    run_cmd(f'cd "{YTUONG_REPO}" && git add . && git commit -m "fix(sync): sync real AI analysis with YouTube for {folder_name}" && git push origin main')
    run_cmd(f'cd "{PORTAL_REPO}" && git add . && git commit -m "fix(sync): sync real AI analysis with YouTube for {folder_name}" && git push origin master')
    print("[+] Đã tự động push cả 2 repo lên GitHub!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync AI Vision Analysis to HTML Reports & YTUONG HUB")
    parser.add_argument("folder_name", help="Tên folder package hoặc đường dẫn")
    parser.add_argument("--shots-file", help="Đường dẫn file json chứa danh sách shot cập nhật (tuỳ chọn)")
    parser.add_argument("--industry", help="ID hoặc tên ngành nghề")
    parser.add_argument("--style", help="ID hoặc kiểu quay")
    parser.add_argument("--tags", help="Danh sách tags phân cách bằng dấu phẩy")
    parser.add_argument("--overview", help="Đoạn trích xuất cốt lõi overview")
    parser.add_argument("--purpose", help="Mục đích cốt lõi")
    parser.add_argument("--custom-headline", help="Custom AI headline")
    parser.add_argument("--script-axis", help="TRỤC KỊCH BẢN 3 NHỊP")
    parser.add_argument("--youtube-url", help="URL YouTube để nhúng iframe")

    args = parser.parse_args()
    sync_analysis(
        args.folder_name,
        shots_update_file=args.shots_file,
        industry=args.industry,
        style=args.style,
        tags=args.tags,
        overview=args.overview,
        purpose=args.purpose,
        custom_headline=args.custom_headline,
        script_axis=args.script_axis,
        youtube_url=args.youtube_url
    )
