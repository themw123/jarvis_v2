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

            
    def ask_wrapper(self, stt):
        return self.__ask_generator(stt)

    def __ask_generator(self, stt):
        try:            
            self.messages.append(
                {"role": "user", "content": stt},
            )
            stream = self.client.chat(
                model=self.server_config["brain"]["ollama"]["model"],
                messages=self.messages,
                stream=True,
                keep_alive=self.server_config["brain"]["ollama"]["keep_alive"],
            )
            
            count = 0
            full_response = ""
            for chunk in stream:
                if Lifecircle.interrupted:
                    break
                if chunk['message']['content'] is not None:
                    if count == 0:
                        #warte sound abspielen
                        #Player.play_wait()
                        pass
                    content = chunk['message']['content']
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
            raise Exception("Ollama: API, failed")

    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)

    def __wakeup_ollama(self):
        print("\n- waking up ollama")
        self.client.chat(
            model=self.server_config["brain"]["ollama"]["model"],
            messages=[{"role": "user", "content": "say \"test\""}],
            keep_alive=self.server_config["brain"]["ollama"]["keep_alive"],
        )