"""Helper launcher for the ResearchPilot Streamlit application."""
import sys
import subprocess
from pathlib import Path

def launch():
    root = Path(__file__).resolve().parent
    venv_streamlit = root / "venv" / "Scripts" / "streamlit.exe"
    app_file = root / "app.py"

    cmd = [str(venv_streamlit), "run", str(app_file), "--server.headless", "true"]
    print(f"Launching ResearchPilot on http://localhost:8501 ...")
    subprocess.run(cmd)

if __name__ == "__main__":
    launch()
