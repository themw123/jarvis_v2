#contextlib um "hello from the pygame community" zu entfernen
import contextlib

from assistant.lifecircle import Lifecircle
with contextlib.redirect_stdout(None):
    from pygame import mixer
    
import io
import queue
import wave
import pyaudio

from pygame import mixer
from pydub import AudioSegment
from gtts import gTTS



class Player:
    
    audio_queue = queue.Queue()
    queing = False


    def __init__(self, config):
        self.config = config
        mixer.init()
    def play_wrapper(self, tts):
                
        if self.config["tts"]["active"] == "google":
            self.__stream_with_google(tts)
        elif self.config["tts"]["active"] == "xtts":
            self.__stream_with_xtts(tts)
        elif self.config["tts"]["active"] == "piper":
            #self.__stream_with_piper(tts)
            return
        else:
            raise Exception(self.config["tts"]["active"] + ": This tts api type does not exist")  
             

    def __stream_with_google(self, audio_bytes):
        
        #damit die sprechpausen nicht so lang sind höhere buffer size
        buffer_size = 10000

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=24000,
                        output=True,
                        frames_per_buffer=buffer_size,
                        )
        
          
        for chunk in audio_bytes:
            if Lifecircle.interruppted:
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
        
        #damit die sprechpausen nicht so lang sind höhere buffer size
        buffer_size = 30000

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=24000,
                        output=True,
                        frames_per_buffer=buffer_size,
                        )
        
        for chunk in audio_bytes:            
            if Lifecircle.interruppted:
                return
            # Chunk abspielen
            stream.write(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()
  

        
    @staticmethod    
    def stream_from_file(): 
                        
        while Player.queing or not Player.audio_queue.empty():
            
            if Lifecircle.interruppted:
                break
            
            try:
                file_path = Player.audio_queue.get(timeout=1)
            except queue.Empty: 
                continue
                
                                
            # Load the audio file using wave
            with wave.open(file_path, 'rb') as audio_file:
                Player.pause()
                # Create a PyAudio instance
                p = pyaudio.PyAudio()

                # Open a stream for playback
                stream = p.open(format=p.get_format_from_width(audio_file.getsampwidth()),
                                channels=audio_file.getnchannels(),
                                rate=audio_file.getframerate(),
                                output=True)
                # Read audio data in chunks and write to the stream
                data = audio_file.readframes(1024)
                while data:
                    if Lifecircle.interruppted:
                        break
                    stream.write(data)
                    data = audio_file.readframes(1024)

                Player.audio_queue.task_done()   
                # Stop and close the stream
                stream.stop_stream()
                stream.close()
                # Terminate the PyAudio instance
                p.terminate()
            
            
            
   
    def __stream_with_piper(self, sentences):
 
        ##not working. #TODO
        

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=22050,
                        output=True,
                        )
        
        counter = 0
        for sentence in sentences:   
            if counter == 0:
                Player.pause()          
            for chunk in sentence:
                if Lifecircle.interruppted:
                    break
                stream.write(chunk)
            counter += 1

        stream.stop_stream()
        stream.close()
        p.terminate()               
            
              
            
    @staticmethod
    def kill_queue():
        Player.queing = False
        # Attempt to clear the queue immediately to prevent any further processing
        while not Player.audio_queue.empty():
            try:
                # Try to get an item from the queue without waiting
                Player.audio_queue.get_nowait()
            except queue.Empty:
                # If the queue is empty, continue to the next iteration
                continue
            # Mark the task as done in the queue
            Player.audio_queue.task_done()
        

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
