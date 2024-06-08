import json

import colorama
from openai import OpenAI

from assistant.lifecircle import Lifecircle


class Chatgpt:

    def __init__(self, server_config, client_config, self_messages: list):
        self.server_config = server_config
        self.client_config = client_config
        self.messages = self_messages
            
    def ask_wrapper(self, stt):
        return self.__ask_generator(stt)


    
    def __ask_generator(self, stt):
        try:
            client = OpenAI(
                api_key=self.server_config["brain"]["chatgpt"]["api_key"],

            )         
            self.messages.append(
                {"role": "user", "content": stt},
            )
                        
            stream = client.chat.completions.create(
                model=self.client_config["brain"]["openai_model"],
                messages=self.messages,
                stream=True,
            )
            
            full_response = ""
            for chunk in stream:
                if Lifecircle.interrupted:
                    break
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            self.messages.append({'role': 'system', 'content': full_response})
            print()
            self.__reset__colorama()

        except Exception as e:
            raise Exception("ChatGPT: API, failed")
              
    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)
