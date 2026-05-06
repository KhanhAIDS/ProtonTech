import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

prompt_text = "Hoàn thành câu sau bằng một ý tưởng càng vô lý càng tốt: 'Bí quyết duy nhất để sống thọ 300 tuổi là mỗi buổi sáng thức dậy bạn phải nuốt chửng một...'"

temperatures = [0.0, 0.3, 0.7, 1.0]
output_file = "temperature_test_results.log"

def run_experiment():
    print(f"PROMPT: {prompt_text}\n")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO KẾT QUẢ THÍ NGHIỆM TEMPERATURE\n")
        f.write("="*50 + "\n")
        f.write(f"PROMPT: {prompt_text}\n")
        f.write("="*50 + "\n\n")

        for temp in temperatures:
            print(f"Đang gọi API với Temperature = {temp}...")
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_text}],
                    temperature=temp,
                    max_tokens=150
                )
                result = response.choices[0].message.content
                
                f.write(f"=== TEMPERATURE: {temp} ===\n")
                f.write(f"{result}\n")
                f.write("-" * 40 + "\n\n")
                
            except Exception as e:
                print(f"Lỗi ở temp {temp}: {e}")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("LỖI: Chưa cấu hình OPENAI_API_KEY.")
    else:
        run_experiment()