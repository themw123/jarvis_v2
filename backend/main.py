import io
import json
from flask import Flask, Response, request
import speech_recognition as sr

from assistant.brain import Brain
from assistant.stt import Stt
from assistant.tts import Tts

app = Flask(__name__)

# Globale Variable
server_config = None
client_config = None
stt: Stt = None
brain: Brain = None
tts: Tts = None

config_path = "backend/config.json"
with open(config_path, 'r') as f:
    server_config = json.load(f)
    

@app.route('/init', methods=['POST'])
def init():
    global stt, brain, tts
    try:
        client_config = request.json
        
        stt = Stt(server_config, client_config)
        brain = Brain(server_config, client_config)
        tts = Tts(server_config, client_config)
        
        return "init done", 200
    except Exception as e:
        return {"error": "init failed", "details": str(e)}, 500

@app.route('/stt', methods=['POST'])
def endpoint_stt():
    audio = request.get_data()
    rate = int(request.headers.get('rate'))
    sample_width =  int(request.headers.get('sample-width'))
    #stt.stt_wrapper(audio=audio)
    audio_data = sr.AudioData(audio, sample_rate=rate, sample_width=sample_width)

    text = stt.stt_wrapper(audio_data)
    return text

@app.route('/brain', methods=['POST'])
def endpoint_brain():
    data = request.get_json()
    stt = data.get('stt')
    
    stream = brain.brain_wrapper(stt)
    
    def generate():
        for chunk in stream:
            yield chunk

    return Response(generate(), content_type='text/plain')
    
if __name__ == '__main__':
    app.run(debug=True)