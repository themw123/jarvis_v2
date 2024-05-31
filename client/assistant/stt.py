import io
import json
import requests
from speech_recognition import AudioData


class Stt:
    def __init__(self, config):
        self.config = config
        
    def request_backend_stt(self, audio, rate: int, sample_width: int):
        url = self.config["backend"]["url"]+'/stt'  
        headers = {'Content-Type': 'application/octet-stream', 'rate': str(rate), 'sample-width': str(sample_width)}
        
        print("- interpret...")
        response = requests.post(url, headers=headers, data=audio)
        if response.status_code != 200:
            raise SystemExit("- STT failed")
        return response.text


    