import requests


class Lifecircle:
    running = False
    interrupted = False        
        
    @staticmethod    
    def listen_to_interupt_keyboard(recorder, config):
        while True:
            recorder.listen_on_keyboard_interrupt()
            Lifecircle.do_interrupt(config)
    
    @staticmethod
    def do_interrupt(config):
        from assistant.player import Player
        Lifecircle.interrupted = True
        Player.pause()
        Player.play_cancel()
        url = config["backend"]["api"]+'/interrupt'
        headers = {'Content-Type': 'plain/text'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("\n- interrupting failed")