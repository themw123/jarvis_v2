
import time
import colorama
import keyboard



class Interrupt:
    interruppted = False
            
    @staticmethod    
    def listen_to_interupt():
        while True:
            if keyboard.is_pressed('ctrl+x'):
                Interrupt.__do_interrupt()
            #important, otherwise the cpu will be overloaded and whisper stt will be extremely slow     
            time.sleep(0.1)        
            
    @staticmethod
    def __do_interrupt():
        Interrupt.interruppted = True
        from assistant.player import Player
        Player.kill_queue()
        Player.play_wait_pause()