import requests
import json


class Brain:
    
    def __init__(self, config):
        self.config = config
        self.messages = [ {"role": "system", "content": self.config["chat"]["role"]} ]

        
    def request_backend_brain(self, stt):
        url = self.config["backend"]["url"]+'/brain'
        headers = {'Content-Type': 'application/json'}
        data = {'stt': stt} 
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        if response.status_code != 200:
            raise SystemExit("- Brain failed")
        for chunk in response.iter_content(1024):
            if chunk:
                yield chunk.decode('utf-8')+ " " 