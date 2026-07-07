import os
import requests
from dotenv import load_dotenv
load_dotenv()

def text_to_speech_bytes(text: str) -> bytes:
    url = "https://api.deepgram.com/v1/speak"
    
    params = {"model": "aura-luna-en"}
    
    headers = {
        "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {"text": text}
    
    response = requests.post(url, params=params, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"Deepgram TTS failed: {response.status_code} {response.text}")
    
    return response.content

