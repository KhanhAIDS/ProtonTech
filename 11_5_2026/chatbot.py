import os
import tiktoken
from openai import OpenAI

class Chatbot:
    def __init__(self, model="gpt-3.5-turbo", max_tokens=3000, window_size=20):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens
        
        # When summarizing, shrink the retained history down to a safe margin
        self.safe_retained_tokens = int(max_tokens * 0.6) 
        self.warning_threshold = int(max_tokens * 0.85)
        self.window_size = window_size
        
        self.history = [
            {"role": "system", "content": "You are a helpful assistant. Keep answers concise."}
        ]
        
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def _get_message_tokens(self, message):
        """Calculates tokens for a single message including API formatting overhead."""
        return 4 + len(self.encoding.encode(message["content"]))

    def count_tokens(self):
        """Calculates the total token count of the current conversation history."""
        return sum(self._get_message_tokens(msg) for msg in self.history)

    def _trim_window(self):
        """Enforces the sliding window message count limit."""
        while len(self.history) > self.window_size + 1:
            self.history.pop(1)

    def summarize_context(self):
        """Dynamically calculates which messages to summarize based on tokens, respecting conversation boundaries."""
        print("\n[System: Token limit exceeded. Calculating dynamic split...]")
        
        system_prompt = self.history[0]
        current_kept_tokens = self._get_message_tokens(system_prompt)
        
        split_index = 1 # Default: Summarize everything after the system prompt if necessary
        
        # 1. Iterate backwards from the newest message
        for i in range(len(self.history) - 1, 0, -1):
            msg_tokens = self._get_message_tokens(self.history[i])
            
            # If adding this message exceeds our safe retention limit, we must split here.
            if current_kept_tokens + msg_tokens > self.safe_retained_tokens:
                split_index = i + 1
                
                # 2. ROUND TO CONVERSATION LEVEL
                # Shifting the split index by +1 to summarize the user and assistant messages together.
                if split_index < len(self.history) and self.history[split_index]["role"] == "assistant":
                    split_index += 1 
                break
                
            current_kept_tokens += msg_tokens

        # 3. Slice the history
        messages_to_summarize = self.history[1:split_index]
        keep_messages = self.history[split_index:]

        if not messages_to_summarize:
            print("[System: Edge case reached. Single interaction is too large to summarize properly.]")
            return

        text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in messages_to_summarize])
        
        summary_prompt = [
            {"role": "system", "content": "Summarize the following conversation concisely. Capture the key facts, user preferences, and main topics discussed."},
            {"role": "user", "content": text_to_summarize}
        ]

        print("[System: Generating summary via API...]")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=summary_prompt,
            max_tokens=300
        )
        
        new_summary = response.choices[0].message.content

        # Combine the System prompt (with new summary) + Retained recent messages
        self.history[0]["content"] = f"You are a helpful assistant. Prior context summary: {new_summary}"
        self.history = [self.history[0]] + keep_messages

    def chat(self, user_input):
        # Handles a single turn of conversation.
        
        # Prevent immediate crash if pastes a massive text block
        user_tokens = len(self.encoding.encode(user_input))
        if user_tokens > (self.max_tokens * 0.8):
            return f"System Error: Your message is too long ({user_tokens} tokens). Please shorten it."

        self.history.append({"role": "user", "content": user_input})
        
        self._trim_window()
        
        current_tokens = self.count_tokens()
        if current_tokens >= self.max_tokens:
            self.summarize_context()
        elif current_tokens >= self.warning_threshold:
            print(f"\n[Warning: Nearing token limit. Current: {current_tokens}/{self.max_tokens}]")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history
            )
            bot_reply = response.choices[0].message.content
            
            self.history.append({"role": "assistant", "content": bot_reply})
            return bot_reply
            
        except Exception as e:
            self.history.pop() # Rollback
            return f"Error connecting to LLM: {str(e)}"

    def start_terminal(self):
        print("=====================================================")
        print(f"Robust Chatbot Initialized (Model: {self.model})")
        print(f"Max Tokens: {self.max_tokens} | Window Size: {self.window_size}")
        print("=====================================================\n")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']: break
            if not user_input.strip(): continue
                
            reply = self.chat(user_input)
            print(f"\nBot: {reply}\n")
            print(f"(Tokens used: {self.count_tokens()}/{self.max_tokens})")
            print("-" * 50)

if __name__ == "__main__":
    app = Chatbot() 
    app.start_terminal()