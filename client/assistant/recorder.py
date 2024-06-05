import threading
import time
import pyaudio
import speech_recognition as sr
from pynput import keyboard

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

        self.ctrl_pressed = False
        self.x_pressed = False
        self.space_pressed = False
        
        self.recording = False
                
        self.__init_recorder()


 
    def __init_recorder(self):
        # Variables for Pyaudio
        self.stream = self.p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)
    
        
    def __after_recording(self):
        Lifecircle.running = True
        Lifecircle.interrupted = False
        Player.play_record_end()
        self.event.set()



    def __on_press_ctrl_space(self, key):
        try:
            if key == keyboard.Key.ctrl_l:
                self.ctrl_pressed = True
            elif key == keyboard.Key.space:
                self.space_pressed = True
        except AttributeError:
            pass
    
    def __on_release_ctrl_space(self, key):
        try:
            if key == keyboard.Key.ctrl_l:
                self.ctrl_pressed = False
                if self.space_pressed:
                    self.space_pressed = False
                    self.recording = not self.recording
                    return False
            elif key == keyboard.Key.space:
                self.space_pressed = False
                if self.ctrl_pressed:
                    self.ctrl_pressed = False
                    self.recording = not self.recording
                    return False
        except AttributeError:
            pass
        
        
    def __on_press_ctrl_x(self, key):
        try:
            if key == keyboard.Key.ctrl_l:
                self.ctrl_pressed = True
            elif key == keyboard.Key.shift_l:
                self.x_pressed = True
        except AttributeError:
            pass

            
    def __on_release_ctrl_x(self, key):
        try:
            if key == keyboard.Key.ctrl_l:
                self.ctrl_pressed = False
                if self.x_pressed:
                    self.x_pressed = False
                    return False
            elif key == keyboard.Key.shift:
                self.x_pressed = False
                if self.ctrl_pressed:
                    self.ctrl_pressed = False
                    return False
        except AttributeError:
            pass
        
        
    def listen_on_keyboard_interrupt(self):
        listener = keyboard.Listener(
            on_press=self.__on_press_ctrl_x,
            on_release=self.__on_release_ctrl_x)
        listener.start()
        listener.join()  
               

    def listen_on_keyboard(self):         
        while True:
            
            listener1 = keyboard.Listener(
                on_press=self.__on_press_ctrl_space, on_release=self.__on_release_ctrl_space)

            listener2 = keyboard.Listener(
                on_press=self.__on_press_ctrl_space, on_release=self.__on_release_ctrl_space)
            
            while Lifecircle.running:
                time.sleep(0.1)
              
            listener1.start()
            listener1.join()    
            listener2.start()
                    
            self.frames = []
            Player.play_record_start()
            print("- listen...\n")
            
            while self.recording:    
                data = self.stream.read(self.chunk)
                self.frames.append(data)   
    
            audio_data = b''.join(self.frames)
            self.audio = audio_data
            self.__after_recording()
            listener2.join()

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
                            if mode == "interrupt":
                                break
                            Player.play_record_start()
                            print("\n- listen...\n")
                            audio_data = recognizerSpokenText.listen(source)
                            audio_bytes = audio_data.get_wav_data(convert_rate=self.rate, convert_width=self.p.get_sample_size(self.format))
                            self.audio = audio_bytes
                            self.__after_recording()
                            break
                        pass
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        pass
                    
        
        