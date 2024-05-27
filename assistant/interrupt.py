
import colorama
import keyboard



class Interrupt:
    interruppted = False
            
    @staticmethod    
    def listen_to_interupt():
        while True:
            if keyboard.is_pressed('ctrl+x'):
                Interrupt.__do_interrupt()
                break     

            
    @staticmethod
    def __do_interrupt():
        Interrupt.interruppted = True
        from assistant.player import Player
        Player.kill_queue()
        print(colorama.Style.RESET_ALL)
        Player.play_wait_pause()