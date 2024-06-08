import colorama
from groq import Groq

from assistant.lifecircle import Lifecircle


class GroqClass:

    def __init__(self, server_config, client_config, messages: list):
        self.server_config = server_config
        self.client_config = client_config
        self.messages = messages
        self.client = Groq(api_key=self.server_config["brain"]["groq"]["api_key"])

    def ask_wrapper(self, stt):
        return self.__ask_generator(stt)

    def __ask_generator(self, stt):
        try:            
            self.messages.append(
                {"role": "user", "content": stt},
            )
            
            stream = self.client.chat.completions.create(
                model=self.client_config["brain"]["groq_model"],
                messages=self.messages,
                temperature=1,
                max_tokens=2048,
                top_p=1,
                stream=True,
                stop=None,
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
            raise Exception(e)

    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)