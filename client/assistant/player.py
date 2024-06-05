#contextlib um "hello from the pygame community" zu entfernen
import contextlib

from assistant.lifecircle import Lifecircle
with contextlib.redirect_stdout(None):
    from pygame import mixer
    
import io
import pyaudio
from pygame import mixer
from pydub import AudioSegment



class Player:

    def __init__(self, config):
        self.config = config
        mixer.init()
    def play_wrapper(self, tts):
                
        if self.config["tts"]["active"] == "google":
            self.__stream_with_google(tts)
        elif self.config["tts"]["active"] == "xtts":
            self.__stream_with_xtts(tts)
        elif self.config["tts"]["active"] == "piper":
            self.__stream_with_piper(tts)
        else:
            raise Exception(self.config["tts"]["active"] + ": This tts api type does not exist")  
             

    def __stream_with_google(self, audio_bytes):
        
        buffer_size = 10000

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=24000,
                        output=True,
                        frames_per_buffer=buffer_size,
                        )
        
          
        for chunk in audio_bytes:
            if Lifecircle.interrupted:
                break
            # Convert mp3 data to raw audio data
            audio_bytes = AudioSegment.from_mp3(io.BytesIO(chunk))
            audio_bytes = audio_bytes.speedup(playback_speed=1.3)
            raw_data = audio_bytes.raw_data
            stream.write(raw_data)

            

        stream.stop_stream()
        stream.close()
        p.terminate()
      
      
    def __stream_with_xtts(self, audio_bytes):
        
        buffer_size = 10000

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=24000,
                        output=True,
                        frames_per_buffer=buffer_size,
                        )
        
        for chunk in audio_bytes:            
            if Lifecircle.interrupted:
                break
            stream.write(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()
  

    def __stream_with_piper(self, audio_bytes):
        
        p = pyaudio.PyAudio()

        stream = p.open(format=8,
                        channels=1,
                        rate=22050,
                        output=True)
        
        for chunk in audio_bytes:            
            if Lifecircle.interrupted:
                break
            stream.write(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()            
            
        

    @staticmethod
    def play_initial():
        mixer.music.load("client/sound/initial.mp3")
        mixer.music.play()
        
    @staticmethod
    def play_initial2():
        mixer.music.load("client/sound/initial2.wav")
        mixer.music.play()
    
    @staticmethod
    def play_initial3():
        mixer.music.load("client/sound/initial3.wav")
        mixer.music.play()
            
    @staticmethod
    def play_wait():
        mixer.music.load("client/sound/wait.mp3")
        mixer.music.play()
    @staticmethod
    def pause():
        mixer.music.pause()  
        
    @staticmethod
    def play_record_start():
        mixer.music.load("client/sound/recording-start.wav")
        mixer.music.set_volume(0.3) 
        mixer.music.play()
    
    @staticmethod
    def play_record_end():
        mixer.music.load("client/sound/recording-end.wav")
        mixer.music.set_volume(0.3) 
        mixer.music.play()    
