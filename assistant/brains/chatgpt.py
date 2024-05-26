import json

import colorama
from openai import OpenAI

from assistant.player import Player


class Chatgpt:

    def __init__(self, config, config_path):
        self.config = config
        self.config_path = config_path

            
    def ask_wrapper(self, stt):
        return self.__ask_generator(stt)


    
    def __ask_generator(self, stt):
        try:
            client = OpenAI(
                api_key=self.config["brain"]["chatgpt"]["api_key"],

            )
            
            messages = [ {"role": "system", "content": self.config["chat"]["role"]} ]
            messages.append(
                {"role": "user", "content": stt},
            )
                        
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True,
            )
            
            count = 0
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    if count == 0:
                        #warte sound abspielen
                        Player.play_wait()
                    count += 1
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    yield content
                    

            print()
            #warte sound pausieren(findet in tts statt)
            #Player.play_wait_pause()
            self.__reset__colorama()

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            raise Exception("ChatGPT: API, failed")


    def __set_conversation_id(self, id):

        # Schritt 1: JSON-Datei laden
        with open(self.config_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Schritt 2: Eintrag bearbeiten
        data["brain"]["chatgpt"]["private"]["memory"]["id"] = id

        # Schritt 3: Aktualisierte Daten in die JSON-Datei schreiben
        with open(self.config_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)  
        
        #aktualisiert automatisch die conversations id der aktuellen conversation. ist ein objekt welches ein verweis ist deshalb atualisiert es auch die conversations_id im Chatbot objekt
        self.memory_id = id
              
    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)
