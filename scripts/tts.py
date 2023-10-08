from pathlib import Path
from tqdm import tqdm
import argparse
from TTS.api import TTS

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)

    args = parser.parse_args()

    tts = TTS("tts_models/fin/fairseq/vits")


    with open(args.input, "r", encoding="utf-8") as f:
        lines = f.readlines()
    text = "".join(lines)
    print(text)
    tts.tts_to_file(text=text,
                    file_path=args.output)