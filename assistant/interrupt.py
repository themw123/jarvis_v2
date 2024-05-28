
import keyboard



class Interrupt:
    interruppted = False
            
    @staticmethod    
    def listen_to_interupt():
        keyboard.add_hotkey('ctrl+x', Interrupt.__do_interrupt)    

    
    @staticmethod
    def __do_interrupt():
        Interrupt.interruppted = True
        from assistant.player import Player
        Player.kill_queue()
        Player.play_wait_pause()