
from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import argparse
import os
from pathlib import Path


def main(args):

    stream_A = True # Start with stream A

    while True:
        # Open stream

        if stream_A:
            source = args["input_A"]
            print("\n\n\n STREAM A \n\n\n")
        else:
            source = args["input_B"]
            print("\n\n\n STREAM B \n\n\n")


        # define required FFmpeg optimizing parameters for your writer
        # [NOTE]: Added VIDEO_SOURCE as audio-source
        # [WARNING]: VIDEO_SOURCE must contain audio

        # while True:
        while True:
            stream = CamGear(source=source, logging=True).start()
            print(f"Streaming from {source}")
            output_params = {
                "-ffpreheaders": ["-re"],
                "-i": source,
                "-acodec": "aac",
                "-ar": 44100,
                "-b:a": 712000,
                "-vcodec": "libx264",
                "-preset": "medium",
                "-b:v": "4500k",
                "-bufsize": "512k",
                "-pix_fmt": "yuv420p",
                "-f": "flv",
            }

            # Define writer with defined parameters and
            writer = WriteGear(
                output="rtmp://localhost/stream",
                logging=True,
                custom_ffmpeg=r"C:\Users\mikko\miniconda3\envs\merisaa-env\Library\bin\ffmpeg.exe",
                **output_params
            )

            # loop over
            while True:

                # read frames from stream
                frame = stream.read()

                # check for frame if Nonetype
                if frame is None:
                    break

                # {do something with the frame here}

                # write frame to writer
                writer.write(frame)

            # safely close video stream
            stream.stop()

            # safely close writer
            writer.close()

            # Check if we need to change the source file
            if Path("CAN_SWITCH").exists():
                stream_A = not stream_A # Switch source
                os.remove("CAN_SWITCH") # Remove the interprocess communication file
                print("SWITCHING THE FILE")
                break


if __name__ == "__main__":

    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_A",
                    "-iA",
                    default="out.mp4",
                    help="Enter your input video file path here.")
    
    ap.add_argument("--input_B",
                    "-iB",
                    default="out.mp4",
                    help="Enter your input video file path here.")
    
    ap.add_argument("--key",
                    "-k",
                    required=True,
                    help="Enter your YouTube-Live Stream Key here.")
    
    args = vars(ap.parse_args())

    main(args)