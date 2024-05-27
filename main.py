
import json
import threading

import colorama

from assistant.interrupt import Interrupt


from assistant.brain import Brain
from assistant.player import Player
from assistant.recorder import Recorder
from assistant.tts import Tts
from assistant.stt import Stt


def main():

    print("\n- start assistant...\n")
    
    global config_path, config
    config_path = "config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    colorama.init()
    
    recorder = Recorder()
    player = Player(config)
    
    brain = Brain(config, config_path)

    stt = Stt(config)
    tts = Tts(config)
    

    #Begrüßung starten
    Player.play_initial()
    

    while True:
        #thread listen to interupt
        t = threading.Thread(target=Interrupt.listen_to_interupt)
        t.start()
 
        audio = recorder.listen()
        stt_text = stt.stt_wrapper(audio=audio)

        print_user(stt_text)
        
        print_assistant()
        brain_text = brain.brain_wrapper(stt=stt_text)

        tts_text = tts.tts_wrapper(brain_text=brain_text)
        
        player.play_wrapper(tts=tts_text)
                          
             
def print_user(stt):
    print("\n" + colorama.Fore.YELLOW + "("+ config["chat"]["your_name"] +"):", stt + colorama.Style.RESET_ALL)
    pass
def print_assistant():
    print("\n" + colorama.Fore.GREEN + "("+config["chat"]["role_name"]+"): ", end="")        
    pass


if __name__ == "__main__":
    main()

   
