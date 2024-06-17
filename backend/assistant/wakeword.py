import numpy as np
import openwakeword
from openwakeword.model import Model

class Wakeword:

    def __init__(self, server_config, client_config):
        self.server_config = server_config
        self.client_config = client_config
        print('\n- starting wakeword model')
        
        #embedding_model and melspectrogram are required for openwakeword. It gets downloaded in resources/models in site-packegas of openwakeword
        #did not find a way to change the location. It seems that openwakeword can only load the embedding_model and melspectrogram models from this location
        #openwakeword.utils.download_models(model_names=["embedding_model", "melspectrogram", "alexa_v0.1"])
        openwakeword.utils.download_models(model_names=[])
        # the following makes only sence if we would have all models manually downloaded and placed in a specific folder
        #self.openwakeword = Model(wakeword_models=["E:\models\openwakeword\\alexa_v0.1.onnx"],)
        self.openwakeword = Model(wakeword_models=[self.client_config["openwakeword"]["model"]],)

        
    def wakeword_wrapper(self, audio: bytes):
        return self.__wakeword(audio)
    
    def __wakeword(self, audio: bytes):
        openwakeword_audio = np.frombuffer(audio, dtype=np.int16)
        prediction = self.openwakeword.predict(openwakeword_audio)
        return prediction[self.client_config["openwakeword"]["model"]] 
    