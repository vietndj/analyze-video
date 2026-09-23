import sys, os, json
sys.path.append("/Users/vietmac/Documents/CODE/AI Course/.agents/skills/analyze-video-02/scripts")
from extract_storyboard_02 import upload_youtube_pipeline

video_path = "/Users/vietmac/Documents/CODE/Quản gia/output_packages/IG_@maxryman_DdlVIp9S9zv_day_in_the_life_☕️/DdlVIp9S9zv.mp4"
meta = {
    "title": "Day In The Life ☕️",
    "uploader": "maxryman",
    "webpage_url": "https://www.instagram.com/reel/DdlVIp9S9zv/",
    "duration_seconds": 16,
    "aspect_ratio": "9:16"
}

print(f"Uploading {video_path}...")
result = upload_youtube_pipeline(video_path, meta)
print(json.dumps(result, indent=2))
