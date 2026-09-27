import json
import os

path = '/Users/vietmac/Documents/CODE/Quản gia/output_packages/IG_@framebygeorge_DdhHCL6OOfK_Day_23_learning_cinematography/shot_info.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

analyses = [
    {
        "headline": "Thiết lập bối cảnh ban mai (Establishing Hook Shot)",
        "subject_action": "Chàng trai ngồi bậu cửa uống cà phê, đón nắng sớm xuyên qua bóng cây.",
        "composition_good": "Khung hình chia cắt sáng tối rõ rệt, đổ bóng (shadow) cây lá lên cánh cửa trắng tạo hiệu ứng Gobo tự nhiên rất mộc mạc.",
        "composition_bad": "Vùng bóng tối ở lưng hơi bết.",
        "takeaway": "Tận dụng bóng nắng tự nhiên chiếu qua cây lá để tạo chiều sâu và mood cinematic ngay từ giây đầu.",
        "lighting": "Natural Low-key (Nắng xiên tạo bóng đổ sâu)",
        "shot_type": "Medium Shot / Bán thân"
    },
    {
        "headline": "Đặc tả thời gian & tia nắng (Macro Detail)",
        "subject_action": "Nắng chiếu vệt ngang qua chiếc thớt gỗ và màn hình đồng hồ chỉ 10:54.",
        "composition_good": "Ánh sáng vệt (streak light) làm nổi bật bề mặt gỗ và tạo nhịp điệu thời gian yên bình.",
        "composition_bad": "Khung hình hơi tĩnh.",
        "takeaway": "Chèn cảnh tĩnh vật có nắng chiếu để tạo quãng nghỉ (breathe-out) cho nhịp video.",
        "lighting": "Hard Light (Nắng gắt tạo vệt sáng)",
        "shot_type": "Close-Up"
    },
    {
        "headline": "Đập trứng vào cốc thủy tinh (Action Close-Up)",
        "subject_action": "Tay đập vỏ trứng, lòng đỏ và lòng trắng rơi xuống cốc đong thủy tinh.",
        "composition_good": "Nắng chiếu xuyên qua cốc thủy tinh và lòng đỏ trứng tạo độ trong trẻo (translucent) và bắt sáng cực đẹp.",
        "composition_bad": "Góc quay hẹp, dễ mất nét nếu tay chuyển động nhanh.",
        "takeaway": "Khi quay đồ ăn có nước/thủy tinh, bắt buộc phải có đèn/nắng đánh ngược (backlight) để tôn chất liệu.",
        "lighting": "Backlight / Nắng ngược",
        "shot_type": "Extreme Close-Up"
    },
    {
        "headline": "Hoa hướng dương bắt nắng (B-roll Detail)",
        "subject_action": "Cận cảnh bông hoa hướng dương đang nở rực rỡ bên cửa sổ.",
        "composition_good": "Tông màu vàng rực của hoa cộng hưởng với nắng ấm, tạo cảm giác tươi mới, tràn đầy năng lượng.",
        "composition_bad": "Chi tiết lá hơi chìm vào vùng tối.",
        "takeaway": "Dùng màu sắc rực rỡ tự nhiên làm điểm nhấn thị giác trong không gian tĩnh.",
        "lighting": "Side Lighting",
        "shot_type": "Close-Up"
    },
    {
        "headline": "Đổ trứng vào chảo (Action Blur)",
        "subject_action": "Trứng được đổ từ cốc vào chảo đen. Khung hình làm mờ (blur) chuyển động của dòng trứng.",
        "composition_good": "Tạo cảm giác chuyển động nhanh, tương phản màu vàng của trứng trên nền chảo đen tối.",
        "composition_bad": "Mất nét (Out of focus) khá nặng ở nửa đầu shot.",
        "takeaway": "Sử dụng chuyển động làm mờ (Motion Blur) có chủ đích để tăng tốc nhịp điệu (Breathe-In).",
        "lighting": "Low-key",
        "shot_type": "Close-Up"
    },
    {
        "headline": "Xúc trứng lên bánh mì (Cinematic Food)",
        "subject_action": "Trứng bác vàng óng được xúc đặt lên lát bánh mì nướng trên đĩa trắng.",
        "composition_good": "Ánh sáng ven (rim light) hắt lên kết cấu xốp của trứng và mặt bánh mì, trông cực kỳ ngon mắt.",
        "composition_bad": "Nền xung quanh tối đen hoàn toàn có thể làm khung cảnh hơi ngột ngạt.",
        "takeaway": "Đánh sáng ven vát (Rim light) là chìa khóa để làm nổi bật kết cấu (texture) của đồ ăn.",
        "lighting": "Chiaroscuro / Rim Light",
        "shot_type": "Close-Up"
    },
    {
        "headline": "Thành phẩm bốc khói (Master Food Shot)",
        "subject_action": "Đĩa bánh mì trứng xịt tương cà được đặt lên bàn gỗ, khói nóng bốc lên nghi ngút trước background sofa xanh.",
        "composition_good": "Khói bốc lên được bắt sáng rõ nhờ backlight. Màu vàng của trứng, đỏ của tương cà và xanh của sofa tạo vòng thuần sắc hoàn hảo.",
        "composition_bad": "Nửa trái khung hình hơi trống.",
        "takeaway": "Luôn tìm cách bắt khói (bằng backlight) để tạo độ \"tươi nóng\" cho món ăn.",
        "lighting": "Backlight / Window Light",
        "shot_type": "Medium Close-Up"
    },
    {
        "headline": "Bóng nắng qua ô cửa (Atmospheric B-roll)",
        "subject_action": "Bóng khung cửa sổ và rèm hạt nhựa in đậm lên bức tường trắng.",
        "composition_good": "Tận dụng hình học của bóng đổ (Shadow geometry) tạo mảng miếng thị giác thú vị mà không cần tốn đồ vật setup.",
        "composition_bad": "Hơi dư sáng (overexposed) ở góc phải dưới.",
        "takeaway": "Đừng bỏ qua các vệt nắng in trên tường, đó là B-roll tuyệt vời nhất về không gian.",
        "lighting": "Hard Sunlight",
        "shot_type": "Medium Shot"
    },
    {
        "headline": "Tán cây ngoài cửa sổ (Depth of Field)",
        "subject_action": "Góc nhìn xuyên qua khung cửa sổ (out of focus) ra tán lá xanh ngoài vườn.",
        "composition_good": "Dùng khung cửa làm tiền cảnh (Foreground) xóa phông, tạo chiều sâu 3D cho cảnh vật tĩnh.",
        "composition_bad": "Lá cây hơi rối mắt.",
        "takeaway": "Dùng tiền cảnh (Foreground) out-of-focus để đóng khung chủ thể (Framing) và tăng chiều sâu không gian.",
        "lighting": "Natural Daylight",
        "shot_type": "Medium Shot"
    }
]

for i, shot in enumerate(data):
    if i < len(analyses):
        update_data = analyses[i]
        # Update top-level
        shot['headline'] = update_data['headline']
        shot['subject_action'] = update_data['subject_action']
        shot['composition_good'] = update_data['composition_good']
        shot['composition_bad'] = update_data['composition_bad']
        shot['takeaway'] = update_data['takeaway']
        shot['shot_type'] = update_data['shot_type']
        shot['lighting'] = update_data['lighting']
        
        # Update analysis object if exists
        if 'analysis' in shot:
            shot['analysis']['headline'] = update_data['headline']
            shot['analysis']['subject_action'] = update_data['subject_action']
            shot['analysis']['composition_good'] = update_data['composition_good']
            shot['analysis']['composition_bad'] = update_data['composition_bad']
            shot['analysis']['takeaway'] = update_data['takeaway']
            shot['analysis']['shot_type'] = update_data['shot_type']
            shot['analysis']['lighting'] = update_data['lighting']

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated shot_info.json successfully!")
