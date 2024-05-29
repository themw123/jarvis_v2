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
    
    def __before_recording(self):
        Interrupt.do_interrupt()
        
    def __after_recording(self):
        Interrupt.interruppted = False
        Player.play_record_end()
        
    def __end_recording(self):
        self.event.set()
        
    

    def listen_on_keyboard(self, config):
        while True: 
            # cool down. Otherwise the space key is recognized immediately from last round
            time.sleep(1)       
            #keyboard.wait('ctrl+space', suppress=True, trigger_on_release=True)
            #deswegen lieber mit schleife
            while not keyboard.is_pressed(config["recorder"]["startkey"]):
                time.sleep(0.1)
            # warte bis space nicht mehr gedrückt ist
            while keyboard.is_pressed(config["recorder"]["startkey"]):
                time.sleep(0.1)
    
            self.frames = []
    
            self.__before_recording()
            Player.play_record_start()
            print("- listen...")
            while not keyboard.is_pressed(config["recorder"]["startkey"]):
                # Record data audio data
                data = self.stream.read(self.chunk)
                # Add the data to a buffer (a list of chunks)
                self.frames.append(data)
            self.__after_recording()
            
            audio_data = b''.join(self.frames)
            self.audio = sr.AudioData(audio_data, sample_rate=self.rate, sample_width=self.p.get_sample_size(self.format))
            #return audio
            self.__end_recording()

    def listen_on_voice(self, mode):
        while True:
            startword = self.config["recorder"]["startword"]
            stopword = self.config["recorder"]["stopword"]
    
            if mode == "interrupt":
                startword = stopword
            
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
                        if startword.lower() in text.lower():
                            #if it is ready to record voice again but is still talking from the last round
                            # not needed in listen_on_keyboard because there interrupting is handlet by the Interrupt listener
                            #Interrupt.do_interrupt()
                            
                            self.__before_recording()
                            if mode == "interrupt":
                                break
                            Player.play_record_start()
                            print("- listen...")
                            audio_data = recognizer.listen(source)
                            self.audio = audio_data
                            self.__after_recording()
                            self.__end_recording()
                            break
                        #print("Du hast gesagt: " + text)
                        pass
                    except sr.UnknownValueError:
                        #print("Google Web Speech API konnte das Audio nicht verstehen")
                        pass
                    except sr.RequestError as e:
                        #print("Konnte keine Anfrage an den Google Web Speech API stellen; {0}".format(e))
                        pass
                    
        
        