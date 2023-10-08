from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import argparse

def main(args):

    # Open stream
    stream = CamGear(source=args['input'], logging=True).start()

    # define required FFmpeg optimizing parameters for your writer
    # [NOTE]: Added VIDEO_SOURCE as audio-source
    # [WARNING]: VIDEO_SOURCE must contain audio
    output_params = {
        "-i": args['input'],
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
        output="rtmp://a.rtmp.youtube.com/live2/{}".format(args['key']),
        logging=True,
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

if __name__ == "__main__":

    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--input",
                    "-i",
                    default="out.mp4",
                    help="Enter your input video file path here.")
    
    ap.add_argument("--key",
                    "-k",
                    required=True,
                    help="Enter your YouTube-Live Stream Key here.")
    
    args = vars(ap.parse_args())

    main(args)