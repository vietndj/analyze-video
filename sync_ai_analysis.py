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

def sync_analysis(folder_name_or_path, shots_update_file=None, industry=None, style=None, tags=None, overview=None, purpose=None, custom_headline=None, script_axis=None):
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
        shooting_style=style
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
            target_key = None
            for k in [shortcode, folder_name]:
                if k in cfgs:
                    target_key = k
                    break
            if target_key:
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
                with open(cfg_path, "w", encoding="utf-8") as f:
                    json.dump(cfgs, f, ensure_ascii=False, indent=2)
                print(f"[+] Đã cập nhật master_classifications.json tại {r}")

    # Rebuild ý tưởng hub
    run_cmd(f'python3 "{YTUONG_REPO}/build_ideas_bank.py"')
    print("[+] Đã build lại ideas_bank trên YTUONG HUB")

    # Auto push
    run_cmd(f'cd "{YTUONG_REPO}" && git add . && git commit -m "fix(sync): sync real AI analysis for {folder_name}" && git push origin main')
    run_cmd(f'cd "{PORTAL_REPO}" && git add . && git commit -m "fix(sync): sync real AI analysis for {folder_name}" && git push origin master')
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
        script_axis=args.script_axis
    )
