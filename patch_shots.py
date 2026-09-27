import json

path = "/Users/vietmac/Documents/CODE/Quản gia/output_packages/IG_@iamaayushswamy_DdpxcaOMaQS_caption_placement/shot_info.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Update shot 1
data[0]["transition"] = "Góc máy Top-Down 90 độ (Đột phá góc nhìn) | Nhịp độ 3.34s (Hơi chớm ngưỡng 3s nhưng có hành động bóc sách bù đắp) | Toàn cảnh (Breathe-Out: Mỏ neo không gian)"

# Update shot 2
data[1]["transition"] = "Góc máy đổi >60 độ so với shot trước (Chống Jump Cut) | Nhịp độ 1.88s (Tuyệt vời <3s) | Cận cảnh (Breathe-In: Kéo sát khoảng cách tâm lý)"

# Update shot 3
data[2]["transition"] = "Đổi trục trực diện >45 độ | Nhịp độ 1.5s (Cực nhanh) | Cận cảnh (Breathe-In liên tiếp: Ép phê thông điệp chữ trên đầu)"

# Update shot 4
data[3]["transition"] = "Xoay góc chéo 30 độ | Nhịp độ 1.13s | Cận cảnh (Breathe-In: Nhoài người Lean-in tạo sự riêng tư)"

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Patched shot_info.json")
