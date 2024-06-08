import re
from assistant.brains.chatgpt import Chatgpt
from assistant.brains.ollama import Ollama
from assistant.brains.groq import GroqClass

class Brain:
    
    def __init__(self, server_config, client_config):
        self.server_config = server_config
        self.client_config = client_config
        self.messages = [ {"role": "system", "content": self.client_config["chat"]["role"]} ]
        self.ollama = Ollama(server_config, client_config, self.messages)
        self.groq = GroqClass(server_config, client_config, self.messages)
        self.chatgpt = Chatgpt(server_config, client_config ,self.messages)

        
    def brain_wrapper(self, stt):
        if self.client_config["brain"]["active"] == "ollama":
            return self.__stream_sentences_from_chunks(self.ollama.ask_wrapper(stt=stt))
        elif self.client_config["brain"]["active"] == "groq":
            return self.__stream_sentences_from_chunks(self.groq.ask_wrapper(stt=stt))
        elif self.client_config["brain"]["active"] == "chatgpt":
            return self.__stream_sentences_from_chunks(self.chatgpt.ask_wrapper(stt=stt))
        else:
            raise Exception(self.client_config["brain"]["active"] + ": This brain type does not exist")
        
    def __stream_sentences_from_chunks(self, chunks_stream):        
        #return/yield every x sententes
        buffer = ''
        self.full_response = ''
        sentence_endings = re.compile(r'(?<=[.!?])\s+|(?<=\n)')
        sentences = []
        
        if self.client_config["tts"]["active"] == "google":
            amount_sentences = self.server_config["tts"]["google"]["amount_input_sentences"]
        elif self.client_config["tts"]["active"] == "xtts":
            amount_sentences = self.server_config["tts"]["xtts"]["amount_input_sentences"]
        elif self.client_config["tts"]["active"] == "piper":
            amount_sentences = self.server_config["tts"]["piper"]["amount_input_sentences"]

        for chunk in chunks_stream:
            buffer += chunk
            self.full_response += chunk

            while True:
                match = sentence_endings.search(buffer)
                if match:
                    sentence = buffer[:match.end()]
                    buffer = buffer[match.end():]
                    if sentence.strip():
                        sentences.append(sentence.strip())
                        if len(sentences) == amount_sentences:
                            yield ' '.join(sentences)
                            sentences = []
                else:
                    break

        # Yield any remaining content in the buffer as a sentence
        if sentences or buffer.strip():
            if buffer.strip():
                sentences.append(buffer.strip())
            yield ' '.join(sentences)
            sentences = []