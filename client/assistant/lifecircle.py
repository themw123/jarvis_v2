



class Lifecircle:
    running = False
    interruppted = False        
        
    @staticmethod    
    def listen_to_interupt_keyboard(config):
        #keyboard.add_hotkey(config["recorder"]["stopkey"], Lifecircle.do_interrupt)  
        pass
    @staticmethod    
    def listen_to_interupt_voice(recorder):
        while True:
            recorder.listen_on_voice("interrupt")
            print("\n\nstoppe")
            Lifecircle.do_interrupt()
    
    @staticmethod
    def do_interrupt():
        Lifecircle.interruppted = True
        from assistant.player import Player
        Player.kill_queue()
        Player.pause()