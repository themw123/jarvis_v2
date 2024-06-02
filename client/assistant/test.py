import websocket

class Tts:
    
    def __init__(self, config):
        self.config = config
        self.websocket = None
        self.ping_interval = 10
        
    def connect(self):
        self.websocket = websocket.create_connection(self.config["backend"]["websocket"])
        print("connected")

    def send(self, message):
        for char in message:
            if char == "__END__":
                break
            self.websocket.send(char)
    
    def receive(self):
        while True:
            message = self.websocket.recv()
            if "__END__" in message:
                break
            elif "__PONG__" in message:
                print("received pong")
                continue
            yield message
    
    def send_ping(self):
        print('!!!!!!!start ping loop!!!!!!!!')
        while True:
            print('ping')
            #if self.websocket:
            #    self.websocket.send("__PING__")
            #time.sleep(self.ping_interval)

    def close(self):
        self.websocket.close()

    def request_backend_tts(self, brain_text):
        self.send(brain_text)
        for char in self.receive():
            yield char.decode("utf-8")