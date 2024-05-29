import colorama
from groq import Groq

from assistant.lifecircle import Lifecircle
from assistant.player import Player


class GroqClass:

    def __init__(self, config, messages: list):
        self.config = config
        self.messages = messages
        self.client = Groq(api_key=self.config["brain"]["groq"]["api_key"])

    def ask_wrapper(self, stt):
        return self.__ask_generator(stt)

    def __ask_generator(self, stt):
        try:            
            self.messages.append(
                {"role": "user", "content": stt},
            )
            
            stream = self.client.chat.completions.create(
                model=self.config["brain"]["groq"]["model"],
                messages=self.messages,
                temperature=1,
                max_tokens=2048,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            count = 0
            full_response = ""
            for chunk in stream:
                if Lifecircle.interruppted:
                    break
                if chunk.choices[0].delta.content is not None:
                    if count == 0:
                        #warte sound abspielen
                        Player.play_wait()
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end="", flush=True)
                    yield content
                    count += 1             
            self.messages.append({'role': 'system', 'content': full_response})
            print()
            self.__reset__colorama()

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            raise Exception("Groq: API, failed")

    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)