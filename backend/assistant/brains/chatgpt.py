import json

import colorama
from openai import OpenAI

from assistant.lifecircle import Lifecircle


class Chatgpt:

    def __init__(self, server_config, self_messages: list):
        self.server_config = server_config
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
                model="gpt-4o",
                messages=self.messages,
                stream=True,
            )
            
            count = 0
            full_response = ""
            for chunk in stream:
                if Lifecircle.interruppted:
                    break
                if chunk.choices[0].delta.content is not None:
                    if count == 0:
                        #warte sound abspielen
                        #Player.play_wait()
                        pass
                    content = chunk.choices[0].delta.content
                    full_response += content
                    #print(content, end="", flush=True)
                    yield content
                    count += 1
            self.messages.append({'role': 'system', 'content': full_response})
            print()
            self.__reset__colorama()

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            raise Exception("ChatGPT: API, failed")
              
    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)
