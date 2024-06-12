import os
import pickle
import platform
import queue
import subprocess
import tempfile

import wave
from gtts import gTTS
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
        
        self.xtts_model = None
        self.xtts_speaker_embedding = None
        self.xtts_gpt_cond_latent = None
        
        if self.client_config["tts"]["active"] == "xtts":
            self.__tts__xtts_init()
            #wake up the model
            for byte in self.__tts_xtts_gen("wakeup"):
                pass
        elif self.client_config["tts"]["active"] == "piper":
            self.__tts_piper_init()
            #wake up the model
            for byte in self.__tts_piper_gen("wakeup"):
                pass
        
        try:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            temp_audio_path = os.path.abspath(os.path.join(current_dir, "..", "temp_audio"))
            if 'build' in current_dir:
                temp_audio_path = os.path.abspath(os.path.join(current_dir, "..", "..","temp_audio"))
            files = os.listdir(temp_audio_path) 
            for file in files:
                os.remove(os.path.join(temp_audio_path, file))     
        except Exception as e:
            raise Exception(e)
            
    def tts_wrapper(self, brain_text):
        
        if self.client_config["tts"]["active"] == "google":
            return self.__tts_google(brain_text)
        elif self.client_config["tts"]["active"] == "xtts":
            return self.__tts_xtts_gen(brain_text)
        elif self.client_config["tts"]["active"] == "piper":
            return self.__tts_piper_gen(brain_text)
        else:
            raise Exception(self.client_config["tts"]["active"] + ": This tts api type does not exist")  


    
    def __tts_google(self, brain_text):
        stream = gTTS(text=brain_text, lang=self.server_config["tts"]["google"]["language"], slow=False).stream()
        for bytes in stream:
            if Lifecircle.interrupted:
                break
            yield bytes
        
        
    def __tts__xtts_init(self):
        print("\n- starting xtts model ...")
        server_config = XttsConfig()
        server_config.load_json(self.server_config["tts"]["xtts"]["location"] + "/config.json")
        self.xtts_model = Xtts.init_from_config(server_config)
        self.xtts_model.load_checkpoint(server_config, checkpoint_dir=self.server_config["tts"]["xtts"]["location"], use_deepspeed=True)
        self.xtts_model.cuda()
        
        self.xtts_speaker_embedding, self.xtts_gpt_cond_latent = self.__xtts_load_voice()    
        
    def __tts_xtts_gen(self, brain_text):
    
        stream = self.xtts_model.inference_stream(
            brain_text,
            "de",
            self.xtts_gpt_cond_latent,
            self.xtts_speaker_embedding,
            temperature=0.7,
            stream_chunk_size=20
        )
        
        for bytes in stream:
            if Lifecircle.interrupted:
                break
            bytes = bytes.cpu().numpy().tobytes()
            yield bytes  
            
    def __tts_piper_init(self):
        print("\n- starting piper model ...")
        operating_system = platform.system()
        if operating_system == "Windows":
            self.piper_binary = self.server_config["tts"]["piper"]["location"]+"/piper.exe"
        else:
            self.piper_binary = self.server_config["tts"]["piper"]["location"]+"/piper"
            
        voice_path = self.server_config["tts"]["piper"]["location"] +"/voices/"+self.client_config["tts"]["piper_voice"]

        files = os.listdir(voice_path)
        self.piper_model_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.onnx')), None)
        self.piper_json_path = next((os.path.join(voice_path, f) for f in files if f.endswith('.json')), None)

    def __tts_piper_gen(self, brain_text):
        
        #piper-tts on windowws with pip not installable. Using subprocess instead
        #does not support streaming. Therefore, the audio is saved in a temporary file and played afterwards.
        
        if Lifecircle.interrupted:
            return
        
        current_dir = os.path.dirname(__file__)
        temp_audio_path = os.path.abspath(os.path.join(current_dir,"..", "temp_audio"))
        if 'build' in current_dir:
            temp_audio_path = os.path.abspath(os.path.join(current_dir, "..", "..", "temp_audio"))

        output_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_audio_path, suffix=".wav")
        
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

        with wave.open(output_file.name, 'rb') as audio_file:
            data = audio_file.readframes(1024)
            while data:
                if Lifecircle.interrupted:
                    break
                yield data
                data = audio_file.readframes(1024)        

       
       
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
 
       
        
                 
                 
    def __xtts_load_voice(self):
        filename = self.client_config["tts"]["xtts_voice"]
        try:
            with open(self.server_config["tts"]["xtts"]["location"]+"/voices/" + filename + '_embedding.pkl', 'rb') as f:
                speaker_embedding = pickle.load(f)
            with open(self.server_config["tts"]["xtts"]["location"]+"/voices/" + filename + '_gpt_cond_latent.pkl', 'rb') as f:
                gpt_cond_latent = pickle.load(f)
            return speaker_embedding, gpt_cond_latent
        except:
            raise Exception("File was not found or could not be loaded")  
        
        