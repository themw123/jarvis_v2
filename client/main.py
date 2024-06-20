import json
import os
import threading
import colorama
import requests


from assistant.lifecircle import Lifecircle


from assistant.brain import Brain
from assistant.player import Player
from assistant.recorder import Recorder
from assistant.tts import Tts
from assistant.stt import Stt


def main():
    global config, recorder, player, brain, stt, tts

    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(current_dir, "config.json")

    if 'lib' in current_dir:
        config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "config.json"))

    with open(config_path, 'r') as f:
        config = json.load(f)
        
    print("\n- start assistant...")
    #startkey = config["recorder"]["startkey"]
    #stopkey = config["recorder"]["stopkey"]
    startkey = "ctrl+space"
    stopkey = "ctrl+shift"
    keyword = config["openwakeword"]["model"].split('_v')[0]
    print("\n- start recording by saying '"+keyword+"' or "+ startkey)
    print("- stop recording by saying '"+keyword+"' or "+ stopkey)    
        
    colorama.init()
    
    recorder = Recorder(config)
    player = Player(config)

    brain = Brain(config)
    
    stt = Stt(config)
    tts = Tts(config)

    init_backend()

    listen_keyboard_interupt = threading.Thread(target=Lifecircle.listen_to_interupt_keyboard, args=(recorder, config))
    listen_keyboard_interupt.start()

    listen_keyboard = threading.Thread(target=recorder.listen_on_keyboard)
    listen_keyboard.start()
    
    listen_voice = threading.Thread(target=recorder.listen_on_voice)
    listen_voice.start()
    
    isStartup = True
    while True:
        if not isStartup:
            print("\n- waiting for you...")
        else:
            isStartup = False
        recorder.event.clear()
        recorder.event.wait()    
         
        audio = recorder.audio
    
        
        stt_text = stt.request_backend_stt(audio=audio, rate=recorder.rate, sample_width=recorder.p.get_sample_size(recorder.format))
        print_user(stt_text)
        print_assistant()
        
        brain_text = brain.request_backend_brain(stt=stt_text)
        
            
        tts_text = tts.request_backend_tts(brain_text=brain_text)
        
        player.play_wrapper(tts=tts_text)
        
        Lifecircle.running = False


def init_backend():
    print("\n- init backend...")
    url = config["backend"]["api"] + '/init'    
    headers = {'Content-Type': 'application/json'}
    while True:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(config))
            if response.status_code != 200:
                raise SystemExit("- Init failed")
            else:
                break
        except Exception as e:
            print("- Connection to backend failed. Retrying...")
            continue
            #raise SystemExit
    
                                     
def print_user(stt_text):
    print("\n" + colorama.Fore.YELLOW + "("+ config["chat"]["your_name"] +"):", stt_text + colorama.Style.RESET_ALL)
    pass
def print_assistant():
    print("\n" + colorama.Fore.GREEN + "("+config["chat"]["role_name"]+"): ", end="")        
    pass

if __name__ == "__main__":
    main()

   
