from time import sleep
from TTS.api import TTS
import subprocess
import itertools
from pathlib import Path
import sys

if __name__=="__main__":

    save_A = False
    while True:

        if save_A:
            out_name = "out_A.mp4"
        else:
            out_name = "out_B.mp4"
                
        subprocess.run([sys.executable,
                        "scripts/get_merisaa.py",
                        "--asema_file", "data/rannikkoasemat_litteroitu.txt"])
        
        subprocess.run([sys.executable,
                     "scripts/tts.py",
                     "--input", "out_01_saatiedotus_merenkulkijoille.txt",
                     "--output", "out_01_saatiedotus_merenkulkijoille.wav"])

        subprocess.run([sys.executable,
                     "scripts/tts.py",
                     "--input", "out_02_saa_rannikkoasemilla.wav",
                     "--output", "out_02_saa_rannikkoasemilla.txt"])
        
        subprocess.run(["ffmpeg",
                        "y",
                        "-f", "concat",
                        "-safe", "0",
                        "-i", "concatenate.txt",
                        "-c", "copy",
                        "out_03_full_audio.wav"])

        subprocess.run(["ffmpeg",
                        "-y",
                        "-loop", "1",
                        "-i", "majakka.png",
                        "-i", "out_03_full_audio.wav",
                        "-vcodec", "libx264",
                        "-shortest",
                        out_name])
        
        while Path("CAN_SWITCH").exists():
            # If the file exists already, the streaming process has not catched up
            pass
        
        with open("CAN_SWITCH", "w") as f:
            # Here we create a file that signals the streaming script that
            # a new source file has been created
            pass

        save_A = not save_A
        sleep(1800)