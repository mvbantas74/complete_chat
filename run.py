import subprocess
import sys
import os

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.normpath(os.path.join(current_dir, "complete_chat.py"))

    cmd = [sys.executable, "-m", "streamlit", "run", app_path]

    subprocess.run(cmd)
