
import keyboard



class Interrupt:
    interruppted = False        
        
    @staticmethod    
    def listen_to_interupt_keyboard(config):
        keyboard.add_hotkey(config["recorder"]["startkey"], Interrupt.do_interrupt)  
          
    @staticmethod    
    def listen_to_interupt_voice(recorder):
        while True:
            recorder.listen_on_voice("interrupt")
            Interrupt.do_interrupt()
    
    @staticmethod
    def do_interrupt():
        Interrupt.interruppted = True
        from assistant.player import Player
        Player.kill_queue()
        Player.pause()