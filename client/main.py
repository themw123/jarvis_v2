import json
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

    config_path = "client/config.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    print("\n- start assistant...")
    print("\n- start recording by saying '"+ config["recorder"]["startword"]+"' or "+config["recorder"]["startkey"])
    print("- stop recording by saying '"+config["recorder"]["stopword"]+"' or "+config["recorder"]["stopkey"])    
        
    colorama.init()
    
    recorder = Recorder(config)
    player = Player(config)

    brain = Brain(config)
    
    stt = Stt(config)
    tts = Tts(config)

    #tts.connect()
    
    init_backend()

    Lifecircle.listen_to_interupt_keyboard(config)
    #for voice interrupting with stopword. Only works with headphones on
    t = threading.Thread(target=Lifecircle.listen_to_interupt_voice, args=(recorder,))
    t.start()

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
        
        stt_text = stt.request_backend_stt(audio=audio, rate=recorder.rate, sample_width=recorder.p.get_sample_size(recorder.format))
        print_user(stt_text)
        print_assistant()
        
        brain_text = brain.request_backend_brain(stt=stt_text)
        
            
        tts_text = tts.request_backend_tts(brain_text=brain_text)
        
        
        #for char in tts_text:
        #    print(char, end="", flush=True)
        
        
        player.play_wrapper(tts=tts_text)
        
        Lifecircle.running = False


def init_backend():
    print("\n- init backend...")
    url = config["backend"]["api"] + '/init'
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(config))
        if response.status_code != 200:
            raise SystemExit("- Init failed")
    except Exception as e:
        print("- Connection to backend failed.")
        raise SystemExit
                                     
def print_user(stt_text):
    print("\n" + colorama.Fore.YELLOW + "("+ config["chat"]["your_name"] +"):", stt_text + colorama.Style.RESET_ALL)
    pass
def print_assistant():
    print("\n" + colorama.Fore.GREEN + "("+config["chat"]["role_name"]+"): ", end="")        
    pass

if __name__ == "__main__":
    main()

   
