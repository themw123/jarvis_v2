import json
import requests

            
class Tts:
    
    def __init__(self, config):
        self.config = config
            
    def request_backend_tts(self, brain_text):
        url = self.config["backend"]["url"]+'/tts'  
        headers = {'Content-Type': 'application/json'}
        data = {'brain_text': brain_text} 
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.text