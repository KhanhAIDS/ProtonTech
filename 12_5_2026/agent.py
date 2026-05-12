import os
import json
from openai import OpenAI


def calculate_math(expression: str) -> str:

    try:
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"


class MathSolverAgent:
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.tools = {
            "calculate_math": calculate_math
        }
        
        self.tool_schema = [{
            "type": "function",
            "function": {
                "name": "calculate_math",
                "description": "Tính toán biểu thức toán học. Gọi hàm này khi người dùng yêu cầu giải toán.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Biểu thức toán (VD: '3 * 1.50 + 0.75')"}
                    },
                    "required": ["expression"]
                }
            }
        }]


    def log(self, step, msg):

        print(f"[\033[94m{step.upper()}\033[0m] {msg}")


    def run(self, user_input):
        self.log("Step 1: Input", f"Nhận yêu cầu: '{user_input}'")

        self.log("Step 2: Processing", "Gửi tới LLM để phân tích ý định và chọn công cụ...")
        messages = [
            {"role": "system", "content": "Bạn là một trợ lý giải toán. Luôn dùng công cụ calculate_math khi gặp phép tính. Trả lời bằng tiếng Việt ngắn gọn, rõ ràng."},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_schema,
            tool_choice="auto" 
        )

        response_message = response.choices[0].message

        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            expression = arguments.get("expression")
            
            self.log("Action Route", f"Agent quyết định gọi hàm '{function_name}' với tham số '{expression}'.")

            tool_result = self.tools[function_name](expression)
            self.log("Tool Execution", f"Kết quả từ Python: {tool_result}")

            self.log("Step 3: Formatting", "Gửi kết quả thô lại cho LLM để tổng hợp câu trả lời cuối cùng...")
            
            messages.append(response_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })

            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            return final_response.choices[0].message.content
        else:
            self.log("Action Route", "Không cần dùng tool. Trả lời trực tiếp.")
            return response_message.content