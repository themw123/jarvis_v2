import threading
import time
import requests
from websocket import create_connection

class Tts:
    
    def __init__(self, config):
        self.config = config
        self.websocket = None
        self.ping_interval = 10
        
    def connect(self):
        self.websocket = create_connection(self.config["backend"]["websocket"])
     
        
    def send(self, brain_text):
        for chunk in brain_text:
            if chunk == "__END__":
                self.websocket.send("__END__")
                break
            self.websocket.send(chunk)
            #print(chunk)
        
    def receive(self):
        while True:
            message = self.websocket.recv()
            if isinstance(message, str):
                if message == "__END__":
                    break
            yield message
        
        
    def piper_read_files(self):
        url = self.config["backend"]["api"]+'/tts_piper_read_files'
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code != 200:
            raise SystemExit("- Piper read files failed")
        for tts_bytes in response.iter_content(1024):
            yield tts_bytes
            #print(tts_bytes)         
        
        

    def request_backend_tts(self, brain_text):
        self.connect()
        thread = threading.Thread(target=self.send, args=(brain_text,))
        thread.start()
        #if self.config["tts"]["active"] != "piper":
        for chunk in self.receive():
            yield chunk
        #else:
        #    for chunk in self.piper_read_files():
        #        yield chunk
        thread.join()
        
        
    
