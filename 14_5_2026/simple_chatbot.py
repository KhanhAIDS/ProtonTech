import os
from openai import OpenAI

class SimpleChatbot:
    def __init__(self, system_prompt="You are a helpful assistant."):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

        self.history = [{"role": "system", "content": system_prompt}]

    def chat(self, user_message: str) -> str:

        self.history.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )

        bot_reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": bot_reply})
        
        return bot_reply