import json
import os
import tempfile
from faster_whisper import WhisperModel
from openai import OpenAI
import speech_recognition as sr
from speech_recognition import AudioData, Recognizer

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

class Stt:
    def __init__(self, config):
        self.config = config
        if self.config["stt"]["active"] == "whisper_local":
            print('\n- starting whisper_local model\n')
            device = "cuda" if self.config["stt"]["whisper_local"]["gpu"] else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            self.model = WhisperModel(
                self.config["stt"]["whisper_local"]["location"] + self.config["stt"]["whisper_local"]["model"],
                device=device,
                compute_type=compute_type
            )

    def stt_wrapper(self, audio: AudioData):
        print("- interpret...")
        if self.config["stt"]["active"] == "whisper_local":
            text = self.__stt_whisper_local(audio)
        elif self.config["stt"]["active"] == "whisper":
            text = self.__stt_whisper(audio)
        elif self.config["stt"]["active"] == "google":
            r = Recognizer()
            text = self.__stt_google(r, audio)
        else:
            raise Exception(self.config["stt"]["active"] + ": This stt api type does not exist") 
        
        text = text.replace("\n", "")
        
        return text
    
    def __stt_whisper_local(self, audio: AudioData):

        text = ""

        try:
            # Erstelle eine temporäre Datei und schreibe den Inhalt des Audio-Streams hinein
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio.get_wav_data())
        except Exception as e:
            raise Exception("Temporäre Datei konnte nicht erstellt werden")

        try:
            with open(temp_file.name, "rb") as audio_file:
                segments, info = self.model.transcribe(
                    audio_file,
                    beam_size=5
                )
                for segment in segments:
                    text += segment.text + " "                   
                text = text.strip()
        except IOError as file_error:
            # Exception for file reading errors (e.g., file not found, permissions issue)
            raise Exception("Fehler beim lesen der Temp File:", file_error)
        except Exception as api_error:
            # Exception for API request errors (e.g., network issues, invalid API response)
            raise Exception("Fehler bei der Whisper local:", api_error)
        finally:
            temp_file.close()
            os.remove(temp_file.name)    
                
        return text

    def __stt_whisper(self, audio: AudioData):

        text = None

        try:
            # Erstelle eine temporäre Datei und schreibe den Inhalt des Audio-Streams hinein
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio.get_wav_data())
        except Exception as e:
            raise Exception("Temporäre Datei konnte nicht erstellt werden")

        try:
            with open(temp_file.name, "rb") as audio_file:
                client = OpenAI(
                    api_key=self.config["brain"]["chatgpt"]["api_key"],
                )
                text = client.audio.transcriptions.create(
                    file = audio_file,
                    model = "whisper-1",
                    response_format="text",
                    language=self.config["stt"]["whisper"]["language"]
                )
        except IOError as file_error:
            # Exception for file reading errors (e.g., file not found, permissions issue)
            raise Exception("Fehler beim lesen der Temp File:", file_error)
        except Exception as api_error:
            # Exception for API request errors (e.g., network issues, invalid API response)
            raise Exception("Fehler bei der Whisper API:", api_error)
        finally:
            temp_file.close()
            os.remove(temp_file.name)    
                
        return text
    
    
    def __stt_google(self, r: Recognizer, audio: AudioData):
        text = ""
        try:
            #nur google ist ohne api key.
            text = r.recognize_google(audio, language=self.config["stt"]["google"]["language"])
        except sr.UnknownValueError:
            print("- Sprache konnte nicht erkannt werden.\n")
        except sr.RequestError:
            print("- Fehler beim Abrufen der Spracherkennung.\n")
        return text
    