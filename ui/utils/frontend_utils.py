import requests
from typing import List, Dict, Optional

def post_prompt_to_backend(chat_history: List[Dict], api_endpoint: str, image: Optional[str]) -> Dict:
    payload = {
        "chat_history": chat_history
    }

    response = requests.post(api_endpoint+"/model/", json = payload)

    return response