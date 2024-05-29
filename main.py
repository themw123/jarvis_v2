
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
    global config, recorder, player, brain, stt, tts

    config_path = "config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    print("\n- start assistant...\n")
    print("- start recording by saying '"+ config["recorder"]["startword"]+"' or "+config["recorder"]["startkey"])
    print("- stop recording by saying '"+config["recorder"]["stopword"]+"' or "+config["recorder"]["startkey"]+"\n")    
        
    colorama.init()
    
    recorder = Recorder(config)
    player = Player(config)

    brain = Brain(config, config_path)
    
    stt = Stt(config)
    tts = Tts(config)

    #for keyboard interrupting use start key
    #for voice interrupting with stopword. Only works with headphones on
    t = threading.Thread(target=Interrupt.listen_to_interupt_voice, args=(recorder,))
    t.start()

    #do recorder.listen() in thread
    listen_keyboard = threading.Thread(target=recorder.listen_on_keyboard, args=(config,))
    listen_keyboard.start()
    
    listen_voice = threading.Thread(target=recorder.listen_on_voice, args=("default",))
    listen_voice.start()
    
    Player.play_initial()
    while True:
        print("\n- waiting for you ...")
        recorder.event.clear()
        recorder.event.wait()

        audio = recorder.audio
        
        stt_text = stt.stt_wrapper(audio=audio)
        print_user(stt_text)
        print_assistant()
        
        brain_text = brain.brain_wrapper(stt=stt_text)

        tts_text = tts.tts_wrapper(brain_text=brain_text)
        
        player.play_wrapper(tts=tts_text)
                                     
def print_user(stt_text):
    print("\n" + colorama.Fore.YELLOW + "("+ config["chat"]["your_name"] +"):", stt_text + colorama.Style.RESET_ALL)
    pass
def print_assistant():
    print("\n" + colorama.Fore.GREEN + "("+config["chat"]["role_name"]+"): ", end="")        
    pass

if __name__ == "__main__":
    main()

   
