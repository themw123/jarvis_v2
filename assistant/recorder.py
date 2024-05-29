import threading
import time
import keyboard 
import pyaudio
import speech_recognition as sr

from assistant.lifecircle import Lifecircle
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
        Lifecircle.do_interrupt()
        
    def __after_recording(self):
        Lifecircle.running = True
        Lifecircle.interruppted = False
        Player.play_record_end()
        self.event.set()


        
    

    def listen_on_keyboard(self, config):        
        while True:
            while Lifecircle.running:
                time.sleep(0.1)
              
            #keyboard.wait is buggy  
            #keyboard.wait('ctrl+space', suppress=True, trigger_on_release=True)
            while not keyboard.is_pressed(config["recorder"]["startkey"]):
                time.sleep(0.1)
            # wait till released
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
            
            audio_data = b''.join(self.frames)
            self.audio = sr.AudioData(audio_data, sample_rate=self.rate, sample_width=self.p.get_sample_size(self.format))
            self.__after_recording()

    def listen_on_voice(self, mode):
        recognizerStartword = sr.Recognizer()
        recognizerSpokenText = sr.Recognizer()
        recognizerSpokenText.pause_threshold = self.config["recorder"]["pause_threshold"]
        recognizerSpokenText.non_speaking_duration = self.config["recorder"]["non_speaking_duration"]
        while True:
            startword = self.config["recorder"]["startword"]
            stopword = self.config["recorder"]["stopword"]
    
            if mode == "interrupt":
                startword = stopword

            with sr.Microphone() as source:
                while True:
                    recognizerStartword.adjust_for_ambient_noise(source, duration=1)
                    recognizerSpokenText.adjust_for_ambient_noise(source, duration=1)
                    audio_data = recognizerStartword.listen(source)
                    self.audio = audio_data  
                    try:
                        text = recognizerStartword.recognize_google(audio_data, language="de-DE")
                        if startword.lower() in text.lower():
                            self.__before_recording()
                            if mode == "interrupt":
                                break
                            Player.play_record_start()
                            print("- listen...")
                            audio_data = recognizerSpokenText.listen(source)
                            self.audio = audio_data
                            self.__after_recording()
                            break
                        #print("Du hast gesagt: " + text)
                        pass
                    except sr.UnknownValueError:
                        #print("Google Web Speech API konnte das Audio nicht verstehen")
                        pass
                    except sr.RequestError as e:
                        #print("Konnte keine Anfrage an den Google Web Speech API stellen; {0}".format(e))
                        pass
                    
        
        