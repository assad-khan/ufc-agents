import subprocess
import threading
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

def run_streamlit():
    subprocess.run(["streamlit", "run", "streamlit_app.py", "--server.port", "7860", "--server.address", "0.0.0.0"])

threading.Thread(target=run_streamlit, daemon=True).start()

@app.get("/")
def root():
    return RedirectResponse(url="/")
