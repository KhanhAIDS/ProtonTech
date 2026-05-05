import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

USE_CASES = {
    "sum": {
        "role": "Biên tập viên công nghệ cao cấp",
        "context": "Bản tin tổng hợp các sự kiện công nghệ nổi bật trong tuần dành cho giới chuyên môn.",
        "instruction": "Tóm tắt các điểm chính của đoạn tin tức sau thành các ý ngắn gọn.",
        "json_schema": '{"key_points": ["point 1", "point 2"], "topic": "string"}',
        "input": "Tập đoàn công nghệ XYZ vừa chính thức công bố mô hình ngôn ngữ lớn thế hệ mới. Phiên bản này giảm 50% chi phí vận hành nhưng lại cải thiện đáng kể khả năng suy luận logic và xử lý toán học phức tạp so với thế hệ tiền nhiệm."
    },
    "class": {
        "role": "Chuyên viên phân tích hệ thống chăm sóc khách hàng",
        "context": "Hệ thống phân loại tự động các phản hồi và khiếu nại của người dùng từ cửa hàng ứng dụng.",
        "instruction": "Phân loại lỗi hệ thống dựa trên mô tả của người dùng.",
        "json_schema": '{"error_category": "Network|UI|Performance|Account", "severity_level": "High|Medium|Low"}',
        "input": "Từ lúc cập nhật phiên bản mới hôm qua, ứng dụng của tôi liên tục bị văng ra ngoài màn hình chính mỗi khi tôi cố gắng mở phần giỏ hàng để thanh toán."
    },
    "ext": {
        "role": "Kỹ sư dữ liệu phần cứng",
        "context": "Cơ sở dữ liệu tự động cập nhật thông số linh kiện từ các bài báo cáo đánh giá thiết bị.",
        "instruction": "Trích xuất các thông số kỹ thuật phần cứng được nhắc đến.",
        "json_schema": '{"component_name": "string", "clock_speed": "string", "power_draw": "string"}',
        "input": "Trong bài kiểm tra hiệu năng, bộ vi xử lý AMD Ryzen 9 7950X đạt mức xung nhịp tối đa lên tới 5.7 GHz, tuy nhiên mức tiêu thụ điện năng cũng khá cao, chạm ngưỡng 230W khi hoạt động hết công suất."
    },
    "trans": {
        "role": "Chuyên gia bản địa hóa phần mềm",
        "context": "Tài liệu hướng dẫn tối ưu hóa cơ sở dữ liệu phân tán cho các lập trình viên nội bộ.",
        "instruction": "Dịch đoạn tài liệu kỹ thuật sau sang tiếng Việt.",
        "json_schema": '{"original_text": "string", "translated_text": "string"}',
        "input": "Implementing a distributed caching layer can significantly reduce database read operations and improve the overall latency of your microservices architecture."
    },
    "gen": {
        "role": "Chuyên viên sáng tạo nội dung tiếp thị",
        "context": "Chiến dịch quảng cáo ra mắt các dòng sản phẩm phụ kiện công nghệ.",
        "instruction": "Sáng tạo 2 câu slogan quảng cáo hấp dẫn cho sản phẩm.",
        "json_schema": '{"slogans": ["slogan 1", "slogan 2"]}',
        "input": "Bàn phím cơ công thái học Alice Pro, thiết kế chia đôi giúp giảm đau mỏi cổ tay, sử dụng switch tĩnh âm phù hợp cho môi trường văn phòng chuyên nghiệp."
    }
}

def build_prompt(uc_data, prompt_type):
    if prompt_type == "full":
        return f"Role: {uc_data['role']}\nInstruction: {uc_data['instruction']}\nContext: {uc_data['context']}\nConstraint: Trả về DUY NHẤT định dạng JSON theo cấu trúc sau: {uc_data['json_schema']}\nInput: {uc_data['input']}"
    
    elif prompt_type == "ricc":
        return f"Role: {uc_data['role']}\nInstruction: {uc_data['instruction']}\nContext: {uc_data['context']}\nInput: {uc_data['input']}"
    
    elif prompt_type == "json":
        return f"{uc_data['instruction']} Trả về định dạng JSON chính xác theo schema này: {uc_data['json_schema']}\n\n{uc_data['input']}"
    
    elif prompt_type == "soft":
        return f"Role: {uc_data['role']}\nInstruction: {uc_data['instruction']}\nContext: {uc_data['context']}\nConstraint: Có thể chọn hoặc không chọn định dạng kết quả dưới dạng JSON {uc_data['json_schema']}.\nInput: {uc_data['input']}"
    
    elif prompt_type == "none":
        return f"{uc_data['instruction']}\nNội dung: {uc_data['input']}"

def validate_response(response_text):
    try:
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return True, data
    except Exception:
        return False, None

def call_llm(prompt_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.1,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("LỖI: Chưa cấu hình OPENAI_API_KEY.")
        exit(1)

    prompt_types = ["full", "ricc", "json", "soft", "none"]
    output_file = "lab_results_matrix.log"
    
    with open(output_file, "w", encoding="utf-8") as f:
        print("Test 25 prompts")
        f.write("So sánh 25 prompts\n" + "="*40 + "\n\n")

        for uc_key, uc_data in USE_CASES.items():
            print(f"\n>> Đang xử lý Use Case: {uc_key.upper()}")
            f.write(f"--- USE CASE: {uc_key.upper()} ---\n")
            f.write(f"Input gốc: {uc_data['input']}\n\n")
            
            for p_type in prompt_types:
                prompt = build_prompt(uc_data, p_type)
                llm_response = call_llm(prompt)
                valid, data = validate_response(llm_response)
                
                f.write(f"[Type: {p_type.upper()}]\n")
                f.write(f"Prompt:\n{prompt}\n")
                f.write(f"Response:\n{llm_response}\n")
                f.write(f"Is_JSON: {valid}\n")
                f.write("-" * 30 + "\n")
                
                print(f"  - [{p_type.upper():<5}] -> JSON hợp lệ: {valid}")

    print(f"\nHoàn tất! Ma trận so sánh đã lưu tại: {output_file}")