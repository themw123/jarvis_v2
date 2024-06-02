import os
import pickle
import platform
import queue
import subprocess
import tempfile
import threading
import time
import wave
from gtts import gTTS
import pyaudio
from assistant.lifecircle import Lifecircle

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

            
class Tts:
    
    def __init__(self, server_config, client_config):
        
        self.server_config = server_config
        self.client_config = client_config
        
        self.piper_queueing = False
        self.piper_file_queue = queue.Queue()
        self.piper_text_queue = queue.Queue()
   
        self.piper_binary = None
        self.piper_model_path = None
        self.piper_json_path = None     
        
        if self.client_config["tts"]["active"] == "xtts":
            print("\n- starting xtts model ...")
            server_config = XttsConfig()
            server_config.load_json(self.server_config["tts"]["xtts"]["location"] + "/config.json")
            self.xtts_model = Xtts.init_from_config(server_config)
            self.xtts_model.load_checkpoint(server_config, checkpoint_dir=self.server_config["tts"]["xtts"]["location"], use_deepspeed=True)
            self.xtts_model.cuda()
        elif self.client_config["tts"]["active"] == "piper":
            self.__tts_piper_init()
        
                
        files = os.listdir("temp_audio")
        for file in files:
            os.remove(os.path.join("temp_audio", file))     
                        
    def tts_wrapper(self, brain_text):
        
        if self.client_config["tts"]["active"] == "google":
            return self.__tts_google(brain_text)
        elif self.client_config["tts"]["active"] == "xtts":
            return self.__tts_xtts(brain_text)
        elif self.client_config["tts"]["active"] == "piper":
            #self.piper_text_queue.put(brain_text)
            return self.__tts_piper_gen(brain_text)
            
      
            
            
            #...
            #return self.__tts_piper_read_files()
        else:
            raise Exception(self.client_config["tts"]["active"] + ": This tts api type does not exist")  


    
    def __tts_google(self, brain_text):
        stream = gTTS(text=brain_text, lang=self.server_config["tts"]["google"]["language"], slow=False).stream()
        for bytes in stream:
            yield bytes
        
        
    def __tts_xtts(self, brain_text):
   
        speaker_embedding, gpt_cond_latent = self.__xtts_load_voice()
        
        stream = self.xtts_model.inference_stream(
            brain_text,
            "de",
            gpt_cond_latent,
            speaker_embedding,
            temperature=0.7,
            stream_chunk_size=20
        )

        for bytes in stream:
            bytes = bytes.cpu().numpy().tobytes()
            yield bytes
            
             
            
    def __tts_piper_init(self):
        operating_system = platform.system()
        if operating_system == "Windows":
            self.piper_binary = self.server_config["tts"]["piper"]["location"]+"/piper.exe"
        else:
            self.piper_binary = self.server_config["tts"]["piper"]["location"]+"/piper"
            
        voice_path = self.server_config["tts"]["piper"]["location"] +"/voices/"+self.server_config["tts"]["piper"]["voice"]

        files = os.listdir(voice_path)
        self.piper_model_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.onnx')), None)
        self.piper_json_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.json')), None)

    def __tts_piper_gen(self, brain_text):
        
        #piper-tts on windowws with pip not installable. Using subprocess instead
        #does not support streaming. Therefore, the audio is saved in a temporary file and played afterwards.

        #for chunk in brain_text:
            
        #if Lifecircle.interruppted:
        #    break

        output_file = tempfile.NamedTemporaryFile(delete=False, dir="./temp_audio", suffix=".wav")
        
        # Construct and execute the Piper TTS command
        command = [
            self.piper_binary,
            "-m", self.piper_model_path,
            "-c", self.piper_json_path,
            "-f", output_file.name
        ]
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.process.communicate(brain_text.encode())
        self.process.wait()
        self.piper_file_queue.put(output_file.name)
        self.piper_queueing = True
        
                

    def tts_piper_read_files(self):
        x = True
        while x:
            while not self.piper_file_queue.empty():
                x = False
                if Lifecircle.interruppted:
                    break
                
                # Load the audio file using wave
                with wave.open(self.piper_file_queue.get(), 'rb') as audio_file:
                    #Player.pause()
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
                        #if Lifecircle.interruppted:
                        #    break
                        #stream.write(data)
                        yield data
                        data = audio_file.readframes(1024)

                    # Stop and close the stream
                    stream.stop_stream()
                    stream.close()
                    # Terminate the PyAudio instance
                    p.terminate()                  

            time.sleep(0.1)
       
       
    def __tts_piper_stream(self, brain_text):
        
        ##not working. #TODO
        
        operating_system = platform.system()
        if operating_system == "Windows":
            piper_binary = self.server_config["tts"]["piper"]["location"]+"/piper.exe"
        else:
            piper_binary = self.server_config["tts"]["piper"]["location"]+"/piper"
            
        voice_path = self.server_config["tts"]["piper"]["location"] +"/voices/"+self.server_config["tts"]["piper"]["voice"]

        files = os.listdir(voice_path)
        model_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.onnx')), None)
        json_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.json')), None)

        for chunk in brain_text:
            # Construct and execute the Piper TTS command
            command = [
                piper_binary,
                "-m", model_path,
                "-c", json_path,
                "--output-raw"
            ]
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            process.stdin.write(chunk.encode())
            process.stdin.close()
            
            while True:
                data = process.stdout.read(1024)
                if not data:
                    break
                yield data
                #print(data)
 
       
        
                 
                 
    def __xtts_load_voice(self):
        filename = self.server_config["tts"]["xtts"]["voice"]
        try:
            with open(self.server_config["tts"]["xtts"]["location"]+"/voices/" + filename + '_embedding.pkl', 'rb') as f:
                speaker_embedding = pickle.load(f)
            with open(self.server_config["tts"]["xtts"]["location"]+"/voices/" + filename + '_gpt_cond_latent.pkl', 'rb') as f:
                gpt_cond_latent = pickle.load(f)
            return speaker_embedding, gpt_cond_latent
        except:
            raise Exception("Datei wurde nicht gefunden oder konnte nicht geladen werden.")  
        
        