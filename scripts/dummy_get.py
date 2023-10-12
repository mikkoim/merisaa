from time import sleep
from TTS.api import TTS
import subprocess
import itertools
from pathlib import Path

TEXT = lambda x: f"Tämä {x} on tekstin {x} alkuosa jotta {x} saadaan vähän {x} lisää täytettä {x} audioon."\
        "testiä testiä vaan {x}"

RANGE = 20

if __name__=="__main__":
    i = 0
    t = ["yksi", "kaksi", "kolme", "neljä", "viisi"]

    tts = TTS("tts_models/fin/fairseq/vits")
    save_A = False
    for text in itertools.cycle(t):

        if save_A:
            out_name = "outtest_A.mp4"
        else:
            out_name = "outtest_B.mp4"
                
        tts.tts_to_file(text=TEXT(text),
                        file_path="outtest.wav")

        subprocess.run(["ffmpeg",
                        "-y",
                        "-loop", "1",
                        "-i", "majakka.png",
                        "-i", "outtest.wav",
                        "-vcodec", "libx264",
                        "-shortest",
                        out_name])
        print(f"{text}")
        i += 1
        while Path("CAN_SWITCH").exists():
            # If the file exists already, the streaming process has not catched up
            pass
        
        with open("CAN_SWITCH", "w") as f:
            # Here we create a file that signals the streaming script that
            # a new source file has been created
            pass

        save_A = not save_A
    
        for j in range(RANGE):
            print(RANGE-j)
            sleep(1)
