import threading
import time
import pyaudio
import speech_recognition as sr
from pynput import keyboard
from websocket import create_connection

from assistant.lifecircle import Lifecircle
from assistant.player import Player

class Recorder:
    
    #init
    def __init__(self, config):
        self.websocket = None
        self.config = config
        self.stream = None
        self.stream_wakeword = None
        self.p = pyaudio.PyAudio()
        self.audio = None
        self.chunk = 1280
        self.rate = 16000
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

        self.stream_wakeword = self.p.open(format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk)
    
        
    def __after_recording(self):
        self.recording = False
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
    
    def __on_release_ctrl_space(self, key, listener):
        try:
            if key == keyboard.Key.ctrl_l:
                self.ctrl_pressed = False
                if self.space_pressed:
                    self.space_pressed = False
                    if listener == "listener2":
                        return False
                    elif not self.recording and not Lifecircle.running:
                        return False
            elif key == keyboard.Key.space:
                self.space_pressed = False
                if self.ctrl_pressed:
                    self.ctrl_pressed = False
                    if listener == "listener2":
                        return False
                    elif not self.recording and not Lifecircle.running:
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
                on_press=self.__on_press_ctrl_space, 
                on_release=lambda key: self.__on_release_ctrl_space(key, "listener1")
            )

            listener2 = keyboard.Listener(
                on_press=self.__on_press_ctrl_space, 
                on_release=lambda key: self.__on_release_ctrl_space(key, "listener2")
            )
            
            while Lifecircle.running:
                time.sleep(0.1)
              
            listener1.start()
            listener1.join()
            self.recording = True    
            listener2.start()
                    
            self.frames = []
            Player.play_record_start()
            print("\n- listen...")
            
            while listener2.is_alive():    
                data = self.stream.read(self.chunk)
                self.frames.append(data) 
                
            audio_data = b''.join(self.frames)
            self.audio = audio_data
            self.__after_recording()

    
    def connect(self):
        url = self.config["backend"]["api"].replace("http://", "ws://")        
        self.websocket = create_connection(url+"/wakeword")
        
        
    def listen_on_voice(self):
        self.connect()
        recognizerSpokenText = sr.Recognizer()
        recognizerSpokenText.pause_threshold = self.config["recorder"]["pause_threshold"]
        recognizerSpokenText.non_speaking_duration = self.config["recorder"]["non_speaking_duration"]
        prediction_has_wakeword = False
        with sr.Microphone() as source:
            print("\n- One time calculating your ambient background noices. Do not say anything...")
            recognizerSpokenText.adjust_for_ambient_noise(source, duration=self.config["recorder"]["ambient_record_time"])
            Player.play_initial()
            print("\n- waiting for you...")
            while True:
                try:
                    self.websocket.send_bytes(self.stream_wakeword.read(self.chunk))
                    prediction = float(self.websocket.recv())
                except Exception as e:
                    print(e)
                    prediction = 0.0
                if prediction > self.config["openwakeword"]["threshold"] and not prediction_has_wakeword: 
                    prediction_has_wakeword = True
                    self.recording = True
                    if Lifecircle.running:
                        Lifecircle.do_interrupt(self.config)
                    while True:
                        try:
                            Player.play_record_start()
                            print("\n- listen...")
                            audio_data = recognizerSpokenText.listen(source)
                            audio_bytes = audio_data.get_wav_data(convert_rate=self.rate, convert_width=self.p.get_sample_size(self.format))
                            self.audio = audio_bytes
                            self.__after_recording()
                            break
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            pass
                elif prediction < 0.01:
                    prediction_has_wakeword = False
            

