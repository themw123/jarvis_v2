import threading
import time
from websocket import create_connection, WebSocketConnectionClosedException

class Tts:
    
    def __init__(self, config):
        self.config = config
        self.websocket = None
        self.connect()
        
    def connect(self):
        self.websocket = create_connection(self.config["backend"]["websocket"])
            
    def send(self, brain_text):
        for chunk in brain_text:
            if chunk == "__END__":
                self.websocket.send("__END__")
                break
            try:
                self.websocket.send(chunk)
            except WebSocketConnectionClosedException:
                self.connect()
                self.websocket.send(chunk)
        
    def receive(self):
        while True:
            try:
                message = self.websocket.recv()
                if isinstance(message, str):
                    if message == "__END__":
                        # temp fix for xtts. Last words are skipped. Strange...
                        time.sleep(1)
                        break
                yield message
            except WebSocketConnectionClosedException:
                self.connect()
                continue

    def request_backend_tts(self, brain_text):
        thread = threading.Thread(target=self.send, args=(brain_text,))
        thread.start()
        for chunk in self.receive():
            yield chunk
        thread.join()
    

