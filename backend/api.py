from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, List

api = FastAPI()

class PromptPost(BaseModel):
    chat_history: List = Field(..., description="the entire chat history")

@api.post('/model/')
def generate_inference(payload: PromptPost):
    pass