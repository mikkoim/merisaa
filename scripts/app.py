import subprocess
import sys
import os
from pathlib import Path
if __name__=="__main__":
    script_dir = Path(os.path.dirname(os.path.realpath(__file__)))

    get_script = script_dir / "dummy_get.py"
    stream_script = script_dir / "dummy_stream.py"

    subprocess.run([sys.executable,
                    str(get_script)])
    subprocess.run([sys.executable,
                    str(stream_script)])