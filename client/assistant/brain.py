import colorama
import requests
import json

from assistant.player import Player


class Brain:
    
    def __init__(self, config):
        self.config = config
        self.messages = [ {"role": "system", "content": self.config["chat"]["role"]} ]

        
    def request_backend_brain(self, stt):
        url = self.config["backend"]["api"]+'/brain'
        headers = {'Content-Type': 'application/json'}
        data = {'stt': stt} 
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        if response.status_code != 200:
            raise SystemExit("- Brain failed")
        Player.play_wait()
        for brain_text in response.iter_content(1024):
            brain_text = brain_text.decode('utf-8') + " "
            if brain_text != "__END__ ":
                Player.pause()
                print(brain_text, end="", flush=True)
            yield brain_text 
        print(colorama.Style.RESET_ALL)