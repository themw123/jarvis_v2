import colorama
from ollama import Client

from assistant.lifecircle import Lifecircle


class Ollama:

    def __init__(self, server_config, client_config, messages: list):
        self.server_config = server_config
        self.client_config = client_config
        self.messages = messages
        if self.client_config["brain"]["active"] == "ollama":
            self.client = Client(host=self.server_config["brain"]["ollama"]["url"])
            self.__wakeup_ollama()

            
    def ask_wrapper(self):
        return self.__ask_generator()

    def __ask_generator(self):
        try:            
            stream = self.client.chat(
                model=self.client_config["brain"]["ollama_model"],
                messages=self.messages,
                stream=True,
                keep_alive=self.server_config["brain"]["ollama"]["keep_alive"],
            )
            
            full_response = ""
            for chunk in stream:
                if Lifecircle.interrupted:
                    break
                if chunk['message']['content'] is not None:
                    content = chunk['message']['content']
                    full_response += content
                    yield content
            self.messages.append({'role': 'system', 'content': full_response})
            print()
            self.__reset__colorama()

        except Exception as e:
            raise Exception(e)

    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)

    def __wakeup_ollama(self):
        print("\n- starting ollama model")
        self.client.chat(
            model=self.client_config["brain"]["ollama_model"],
            messages=[{"role": "user", "content": "say \"test\""}],
            keep_alive=self.server_config["brain"]["ollama"]["keep_alive"],
        )