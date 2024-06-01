import io
import uvicorn
import json
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import speech_recognition as sr

from assistant.brain import Brain
from assistant.stt import Stt
from assistant.tts import Tts

app = FastAPI()

# Globale Variable
server_config = None
client_config = None
stt: Stt = None
brain: Brain = None
tts: Tts = None

config_path = "backend/config.json"
with open(config_path, 'r') as f:
    server_config = json.load(f)
    


@app.post('/init')
async def init(request: Request):
    global stt, brain, tts
    try:
        client_config = await request.json()
        
        stt = Stt(server_config, client_config)
        brain = Brain(server_config, client_config)
        tts = Tts(server_config, client_config)
        
        return {"message": "init done"}
    except Exception as e:
        return {"error": "init failed", "details": str(e)}

@app.post('/stt')
async def endpoint_stt(request: Request):
    audio = await request.body()
    rate = int(request.headers.get('rate'))
    sample_width = int(request.headers.get('sample-width'))
    
    audio_data = sr.AudioData(audio, sample_rate=rate, sample_width=sample_width)

    return stt.stt_wrapper(audio_data)


@app.post('/brain')
async def endpoint_brain(request: Request):
    data = await request.json()
    stt_text = data.get('stt')
    
    stream = brain.brain_wrapper(stt_text)
    
    def generate():
        for chunk in stream:
            yield chunk

    return StreamingResponse(generate(), media_type='text/plain')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)