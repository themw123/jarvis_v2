
import os
import sys
import uvicorn
import json
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import speech_recognition as sr

from assistant.wakeword import Wakeword
from assistant.brain import Brain
from assistant.lifecircle import Lifecircle
from assistant.stt import Stt
from assistant.tts import Tts
from update.updater import Updater

app = FastAPI()

# Globale Variable
server_config = None
client_config = None

Lifecircle.interrupted = False
wakeword: Wakeword = None
stt: Stt = None
brain: Brain = None
tts: Tts = None


current_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(current_dir, "config.json")

program_name = sys.argv[0]
extension = os.path.splitext(program_name)[1]

if extension != ".py":
    config_path = os.path.abspath(os.path.join(current_dir, "..", "..", "config.json"))


with open(config_path, 'r', encoding='utf-8') as f:
    server_config = json.load(f)
        

updater = Updater(server_config, "backend")
updater.run()

@app.post('/init')
async def init(request: Request):
    global wakeword, stt, brain, tts
    try:
        client_config = await request.json()
        
        wakeword = Wakeword(server_config, client_config)
        stt = Stt(server_config, client_config)
        brain = Brain(server_config, client_config)
        tts = Tts(server_config, client_config)
                
        return {"message": "init done"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"error": "init failed", "details": str(e)})
    
@app.get('/interrupt')
async def initerrupt():
    try:
        Lifecircle.interrupted = True
        return {"message": "received interrupted"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"error": "interrupting failed", "details": str(e)})


@app.post('/stt')
async def endpoint_stt(request: Request):
    try:
        Lifecircle.interrupted = False
        audio = await request.body()
        rate = int(request.headers.get('rate'))
        sample_width = int(request.headers.get('sample-width'))
        
        audio_data = sr.AudioData(audio, sample_rate=rate, sample_width=sample_width)
        return stt.stt_wrapper(audio_data)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"error": "stt failed", "details": str(e)})


@app.post('/brain')
async def endpoint_brain(request: Request):
    try:
        data = await request.json()
        stt_text = data.get('stt')
        
        stream = brain.brain_wrapper(stt_text)
        
        def generate():
            for chunk in stream:
                yield chunk
            yield "__END__"  
        return StreamingResponse(generate(), media_type='text/plain')
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"error": "brain failed", "details": str(e)})

@app.websocket("/tts")
async def websocket_tts(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                brain_sentence = await websocket.receive_text()
                
                if brain_sentence.strip() == "__END__":
                    await websocket.send_text("__END__")    
                else:
                    sentence_byte = tts.tts_wrapper(brain_sentence)
                    for bytes in sentence_byte:
                        await websocket.send_bytes(bytes)


            except WebSocketDisconnect:
                break
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"error": "tts failed", "details": str(e)})  
    
    
@app.websocket("/wakeword")
async def websocket_wakeword(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                bytes = await websocket.receive_bytes()
                prediction = wakeword.wakeword_wrapper(bytes)
                await websocket.send_text(str(prediction))
            except WebSocketDisconnect:
                break
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail={"error": "tts failed", "details": str(e)})      

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)