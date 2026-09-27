import json

path1 = "/Users/vietmac/Documents/CODE/ytuong-fedu-vn/master_classifications.json"
path2 = "/Users/vietmac/Documents/CODE/vietndj.github.io/master_classifications.json"

vid_id = "IG_@jigummmmm_DdnqexOTN8A_설거지하는_모습도_예쁘게_찍을_수_있냐고요"
new_title = "Nghệ Thuật Băm Nhỏ Chuyển Động (Micro-Actions) & ASMR B-Roll Đời Thường"

for path in [path1, path2]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if vid_id in data:
            data[vid_id]["custom_headline"] = new_title
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error {path}: {e}")

print("Fixed title in DB")
