from groq import Groq
import os


class ReflectionAgent:

    def __init__(self, model: str = "llama3-70b-8192"): #"llama3-8b-8192"
        self.client = Groq(api_key=os.environ.get("groq_api_key"))
        self.model = model
        self.generation_history = []
        self.reflection_history = []

    def _model(self, role: str, message: str):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": role, "content": message}
            ],
            model=self.model,
        )

        print(chat_completion.choices[0].message.content)

    def generate(self, messages: list):
        return None
    
    def reflect(self):
        return None
    
    def invoke(self, messages: list):
        return None