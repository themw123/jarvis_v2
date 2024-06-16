import threading
import time
from websocket import create_connection

class Tts:
    
    def __init__(self, config):
        self.config = config
        self.websocket = None
        
    def connect(self):
        self.websocket = create_connection(self.config["backend"]["websocket"]+"/tts")
        
            
    def send(self, brain_text):
        for chunk in brain_text:
            if chunk == "__END__":
                self.websocket.send("__END__")
                break
            self.websocket.send(chunk)

        
    def receive(self):
        while True:
            message = self.websocket.recv()
            if isinstance(message, str):
                if message == "__END__":
                    # temp fix for xtts. Last words are skipped. Strange...
                    time.sleep(1)
                    break
            yield message


    def request_backend_tts(self, brain_text):
        #if we instead would use self.connect() in init and catch exception and reconnect with socker in receive and send
        #there would be a problem when interrupting with key combination.
        #create_connect is not the best for our use case.
        #in general: create_connection is not meant to be used with keep-alive connections. It is a wrapper for simple use cases.
        #todo: use websocket instead of create_connection
        self.connect()
        
        thread = threading.Thread(target=self.send, args=(brain_text,))
        thread.start()
        for chunk in self.receive():
            yield chunk
        thread.join()
    

