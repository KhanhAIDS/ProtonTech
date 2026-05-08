import argparse
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load biến môi trường chứa OPENAI_API_KEY
load_dotenv()

# Khởi tạo client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_email(email_text):
    # Gửi email tới LLM và nhận lại kết quả JSON.
    
    system_prompt = """
    Bạn là một trợ lý ảo chuyên nghiệp. Hãy phân tích email và trả về kết quả CHỈ DƯỚI DẠNG JSON.
    Cấu trúc JSON bắt buộc:
    {
        "summary": "Tóm tắt nội dung email ngắn gọn trong 3-5 câu.",
        "action_items": ["Nhiệm vụ 1", "Nhiệm vụ 2"],
        "priority": "High" | "Medium" | "Low",
        "people_mentioned": ["Tên người 1", "Tên người 2"]
    }
    Không bao gồm markdown, không giải thích thêm.
    """

    try:
        # Gọi API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": email_text}
            ],
            temperature=0.2, # Nhiệt độ thấp để output ổn định
            response_format={"type": "json_object"} # Ép chuẩn JSON output
        )
        
        raw_output = response.choices[0].message.content
        
        # Parse JSON để kiểm tra và xử lý lỗi format
        parsed_json = json.loads(raw_output)
        return parsed_json

    except json.JSONDecodeError:
        return {"error": "Lỗi: Output từ AI không phải là JSON hợp lệ."}
    except Exception as e:
        return {"error": f"Lỗi hệ thống hoặc API: {str(e)}"}

def main():
    # Khởi tạo CLI interface
    parser = argparse.ArgumentParser(description="AI Email Summarizer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Nội dung email truyền trực tiếp")
    group.add_argument("--file", type=str, help="Đường dẫn đến file text chứa email")

    args = parser.parse_args()

    # Đọc input
    email_content = ""
    if args.text:
        email_content = args.text
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as file:
                email_content = file.read()
        except FileNotFoundError:
            print(json.dumps({"error": "Không tìm thấy file đầu vào."}, ensure_ascii=False))
            return

    # Xử lý input rỗng
    if not email_content.strip():
        print(json.dumps({"error": "Nội dung email rỗng."}, ensure_ascii=False))
        return

    # Gọi hàm xử lý và in kết quả
    result = summarize_email(email_content)
    print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()