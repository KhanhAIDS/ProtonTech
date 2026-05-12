import os
from agent import MathSolverAgent

if __name__ == "__main__":

    if not os.getenv("OPENAI_API_KEY"):
        print("Lỗi: Chưa cài đặt OPENAI_API_KEY environment variable.")
        print("Vui lòng chạy lệnh: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    agent = MathSolverAgent()

    print(">>> TEST CASE 1: KÍCH HOẠT TOOL")
    user_query_1 = "Nếu tôi mua 3 quả táo giá 15000đ mỗi quả và 1 quả chuối giá 7500đ, tổng cộng tôi phải trả bao nhiêu?"
    print(f"User: {user_query_1}\n")

    final_answer_1 = agent.run(user_query_1)
    
    print(f"\nFINAL OUTPUT: {final_answer_1}\n")
    print("-" * 60 + "\n")

    print(">>> TEST CASE 2: TRẢ LỜI TRỰC TIẾP (KHÔNG DÙNG TOOL)")
    user_query_2 = "Bạn có thể làm được những việc gì?"
    print(f"User: {user_query_2}\n")
    
    final_answer_2 = agent.run(user_query_2)
    
    print(f"\nFINAL OUTPUT: {final_answer_2}\n")