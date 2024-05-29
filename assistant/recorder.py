import threading
import time
import keyboard 
import pyaudio
import speech_recognition as sr

from assistant.interrupt import Interrupt
from assistant.player import Player

class Recorder:
    
    #init
    def __init__(self, config):
        self.config = config
        self.stream = None
        self.p = pyaudio.PyAudio()
        self.audio = None
        self.chunk = 1024
        self.rate = 44100
        self.channels = 1
        self.format = pyaudio.paInt16
        self.frames = []
        
        self.event = threading.Event()

                
        self.__init_recorder()


 
    def __init_recorder(self):
        # Variables for Pyaudio
        self.stream = self.p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
    
    

    def listen_on_keyboard(self):
        Player.pause()
        while True: 
            
            # coll down. Otherwise the space key is recognized immediately from last round
            time.sleep(1)       
                
            #keyboard.wait('ctrl+space', suppress=True, trigger_on_release=True)
            #deswegen lieber mit schleife
            while not keyboard.is_pressed('ctrl + space'):
                time.sleep(0.1)
            # warte bis space nicht mehr gedrückt ist
            while keyboard.is_pressed('ctrl + space'):
                time.sleep(0.1)
            
            
            self.frames = []
            
            Player.kill_queue()
            Player.play_record_start()
            
            # Record audio until space is pressed again to stop
            print("- listen...")
            while not keyboard.is_pressed('ctrl + space'):
                # Record data audio data
                data = self.stream.read(self.chunk)
                # Add the data to a buffer (a list of chunks)
                self.frames.append(data)

            Interrupt.interruppted = False

            Player.play_record_end()
            
            audio_data = b''.join(self.frames)

            self.audio = sr.AudioData(audio_data, sample_rate=self.rate, sample_width=self.p.get_sample_size(self.format))

            #return audio
            self.event.set()

        
    def listen_on_voice(self, mode):
        
        Player.pause()
        
        while True:
 
            keyword = self.config["stt"]["keyword"]
            breakword = self.config["stt"]["breakword"]
            
            if mode == "interrupt":
                keyword = breakword
            
            # Erstelle ein Recognizer-Objekt
            recognizer = sr.Recognizer()

            # Verwende das Mikrofon als Audioquelle
            with sr.Microphone() as source:
                while True:
                    recognizer.adjust_for_ambient_noise(source, duration=3)
                    audio_data = recognizer.listen(source)
                    self.audio = audio_data  
                    try:
                        text = recognizer.recognize_google(audio_data, language="de-DE")
                        if keyword.lower() in text.lower():
                            #if it is ready to record voice again but is still talking from the last round
                            Interrupt.do_interrupt()
                            if mode == "interrupt":
                                break
                            print("- listen...")
                            Player.play_record_start()
                            audio_data = recognizer.listen(source)
                            self.audio = audio_data
                            Player.play_record_end() 
                            Interrupt.interruppted = False
                            self.event.set()
                            break
                        #print("Du hast gesagt: " + text)
                        pass
                    except sr.UnknownValueError:
                        #print("Google Web Speech API konnte das Audio nicht verstehen")
                        pass
                    except sr.RequestError as e:
                        #print("Konnte keine Anfrage an den Google Web Speech API stellen; {0}".format(e))
                        pass
                    
        
        