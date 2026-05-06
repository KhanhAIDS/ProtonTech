import requests
import os

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

instruction = "Phân tích đánh giá. Trả về định dạng: [CẢM_XÚC] [CHỮ_CÁI_ĐẦU] [CẢ_CÂU_ĐÁNH_GIÁ]. Không nói thêm bất kỳ từ nào khác."
input_text = "Cái laptop này pin tụt nhanh kinh khủng, mới rút sạc 1 tiếng đã sập nguồn!"

zero_shot_prompt = f"{instruction}\n\nĐánh giá: {input_text}\nKết quả:"

few_shot_prompt = f"""{instruction}

Đánh giá: Giao hàng chậm, đóng gói móp méo hết cả hộp.
Kết quả: [TỨC_GIẬN] [G] [Giao hàng chậm, đóng gói móp méo hết cả hộp.]

Đánh giá: Màn hình sáng đẹp, nhân viên tư vấn rất nhiệt tình.
Kết quả: [HÀI_LÒNG] [M] [Màn hình sáng đẹp, nhân viên tư vấn rất nhiệt tình.]

Đánh giá: Dùng tạm ổn trong tầm giá, không có gì nổi trội.
Kết quả: [BÌNH_THƯỜNG] [D] [Dùng tạm ổn trong tầm giá, không có gì nổi trội.]

Đánh giá: {input_text}
Kết quả:"""

def call_openrouter(prompt_text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "baidu/qianfan-ocr-fast:free", 
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.0,
        "max_tokens": 50
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        content = response.json()['choices'][0]['message'].get('content')
        return content.strip() if content else "Lỗi: Model trả về kết quả rỗng (None)."
    return f"Lỗi API: {response.status_code} - {response.text}"

if __name__ == "__main__":
    log_filename = "n_shot_prompting_results.log"
    
    with open(log_filename, "w", encoding="utf-8") as f:

        f.write("--- ZERO-SHOT ---\n")
        f.write(call_openrouter(zero_shot_prompt) + "\n\n")
        
        f.write("--- FEW-SHOT ---\n")
        f.write(call_openrouter(few_shot_prompt) + "\n")