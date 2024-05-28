import time
import keyboard 
import pyaudio
import speech_recognition as sr

from assistant.interrupt import Interrupt
from assistant.player import Player


class Recorder:

    #init
    def __init__(self):
        pass
 

    def listen(self):
        
        # Variables for Pyaudio
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100


        # Audio recording stuff
        p = pyaudio.PyAudio()

        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)


        # Create an empty list for audio recording
        frames = []
        #stream schon mal starten

        print("- ctrl + space start/stop recording")
        
        #nach langer wartezeit reagiert es nicht mehr auf ctrl + space
        keyboard.wait('ctrl+space', suppress=True, trigger_on_release=True)
        #deswegen lieber mit schleife
        #while not keyboard.is_pressed('ctrl + space'):
        #    time.sleep(0.1)
        # warte bis space nicht mehr gedrückt ist
        #while keyboard.is_pressed('ctrl + space'):
        #    time.sleep(0.1)

        # stop playing old audio if there is any
        Player.kill_queue()
        Player.play_record_start()
        
        # Record audio until space is pressed again to stop
        print("- listen...")
        while not keyboard.is_pressed('ctrl + space'):
            # Record data audio data
            data = stream.read(chunk)
            # Add the data to a buffer (a list of chunks)
            frames.append(data)


        Interrupt.interruppted = False

        Player.play_record_end()

        # Close the audio recording stream
        stream.close()
        p.terminate()

        # Concatenate the recorded audio data from the list of frames
        audio_data = b''.join(frames)

        # Convert the recorded audio data to a speech_recognition.AudioData object
        #r = sr.Recognizer()

        
        """
        # spiele audio ab zum testen
        sample_width = 2
        audio_seg = AudioSegment(
            data=audio_data,
            sample_width=sample_width, 
            frame_rate=rate,
            channels=channels
        )
        play_pydub(audio_seg)
        """

        audio = sr.AudioData(audio_data, sample_rate=rate, sample_width=p.get_sample_size(format))

        return audio

        

        
        