import os
import tempfile
from faster_whisper import WhisperModel
from openai import OpenAI
import speech_recognition as sr
from speech_recognition import AudioData, Recognizer

from assistant.lifecircle import Lifecircle
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

class Stt:

    def __init__(self, server_config, client_config):
        self.server_config = server_config
        self.client_config = client_config
        if self.client_config["stt"]["active"] == "whisper_local":
            print('\n- starting whisper_local model')
            device = "cuda" if self.server_config["stt"]["whisper_local"]["gpu"] else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            self.model = WhisperModel(
                model_size_or_path=self.server_config["stt"]["whisper_local"]["location"] + self.server_config["stt"]["whisper_local"]["model"],
                device=device,
                compute_type=compute_type
            )
            # wake up the model
            for segment in self.model.transcribe(
                audio="backend/wakeup.wav",
                beam_size=5
            ):
                pass
    


    def stt_wrapper(self, audio: AudioData):
        print("- interpret...")
        if self.client_config["stt"]["active"] == "whisper_local":
            text = self.__stt_whisper_local(audio)
        elif self.client_config["stt"]["active"] == "whisper":
            text = self.__stt_whisper(audio)
        elif self.client_config["stt"]["active"] == "google":
            r = Recognizer()
            text = self.__stt_google(r, audio)
        else:
            raise Exception(self.client_config["stt"]["active"] + ": This stt api type does not exist") 
        
        text = text.replace("\n", "")
        
        return text
    
    def __stt_whisper_local(self, audio: AudioData):

        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio.get_wav_data())
        except Exception as e:
            raise Exception(e)

        try:
            with open(temp_file.name, "rb") as audio_file:
                text = ""
                segments, info = self.model.transcribe(
                    audio_file,
                    beam_size=5
                )
                for segment in segments:
                    if Lifecircle.interrupted:
                        break
                    text += segment.text + " "
                return text.strip()
                
        except IOError as e:
            raise Exception(e)
        except Exception as e:
            raise Exception(e)
        finally:
            temp_file.close()
            os.remove(temp_file.name)  
                
    def __stt_whisper(self, audio: AudioData):

        try:
            # Erstelle eine temporäre Datei und schreibe den Inhalt des Audio-Streams hinein
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio.get_wav_data())
        except Exception as e:
            raise Exception(e)

        try:
            with open(temp_file.name, "rb") as audio_file:
                client = OpenAI(
                    api_key=self.server_config["brain"]["chatgpt"]["api_key"],
                )
                text = client.audio.transcriptions.create(
                    file = audio_file,
                    model = "whisper-1",
                    response_format="text",
                    language=self.server_config["stt"]["whisper"]["language"],
                    
                )
            return text
        except IOError as e:
            raise Exception(e)
        except Exception as e:
            raise Exception(e)
        finally:
            temp_file.close()
            os.remove(temp_file.name)    
                
    
    
    def __stt_google(self, r: Recognizer, audio: AudioData):
        try:
            #nur google ist ohne api key.
            result = r.recognize_google(audio, language=self.server_config["stt"]["google"]["language"])
            if result is not None:
                return result
            else:
                return "" 

        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

    