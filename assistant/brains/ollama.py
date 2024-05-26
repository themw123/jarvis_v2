import colorama
from ollama import Client


from assistant.player import Player


class Ollama:

    def __init__(self, config):
        self.config = config
        if self.config["brain"]["active"] == "ollama":
            self.client = Client(host=self.config["brain"]["ollama"]["url"])
            self.__wakeup_ollama()

            
    def ask_wrapper(self, stt):
        return self.__ask_generator(stt)

    def __ask_generator(self, stt):
        try:            
            messages = [ {"role": "system", "content": self.config["chat"]["role"]} ]
            messages.append(
                {"role": "user", "content": stt},
            )
            
            stream = self.client.chat(
                model=self.config["brain"]["ollama"]["model"],
                messages=messages,
                stream=True,
                keep_alive=self.config["brain"]["ollama"]["keep_alive"],
            )
            
            count = 0
            for chunk in stream:
                if chunk['message']['content'] is not None:
                    if count == 0:
                        #warte sound abspielen
                        Player.play_wait()
                    count += 1
                    content = chunk['message']['content']
                    print(content, end="", flush=True)
                    yield content
                    

            print()
            self.__reset__colorama()

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            raise Exception("Ollama: API, failed")

    def __reset__colorama(self):
        print(colorama.Style.RESET_ALL)

    def __wakeup_ollama(self):
        print("\n- waking up Ollama\n")

        self.client.generate(model=self.config["brain"]["ollama"]["model"],keep_alive=self.config["brain"]["ollama"]["keep_alive"])