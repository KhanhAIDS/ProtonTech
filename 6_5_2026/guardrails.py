import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def validate_json(text):
    try:
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return True, json.loads(clean_text)
    except json.JSONDecodeError:
        return False, None

def check_length(text, max_length=300):
    return len(text) <= max_length

def filter_content(text, forbidden_words=["bạo lực", "hack", "secret"]):
    text_lower = text.lower()
    return not any(word in text_lower for word in forbidden_words)

def call_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

def run_pipeline(prompt, max_retries=3):
    for attempt in range(1, max_retries + 1):
        print(f"\n[Lần thử {attempt}/{max_retries}] Đang gọi LLM...")
        
        output = call_llm(prompt)
        print(f"Kết quả:\n{output}")
        
        is_valid_len = check_length(output)
        is_clean = filter_content(output)
        is_json, json_data = validate_json(output)
        
        if not is_valid_len:
            print("Fail: Quá dài.")
            continue
        if not is_clean:
            print("Fail: Từ khóa nhạy cảm.")
            continue
        if not is_json:
            print("Fail: Không phải JSON.")
            continue
            
        print("SUCCESS!")
        return json_data
            
    print("\nPIPELINE THẤT BẠI.")
    return None

if __name__ == "__main__":
    test_prompt = 'Tạo một JSON gồm 2 trường: "status" (giá trị "ok") và "message" (giá trị "hoàn thành lab"). Chỉ in ra JSON, không giải thích.'
    final_result = run_pipeline(test_prompt)
    
    if final_result:
        print(type(final_result))
        print(final_result)