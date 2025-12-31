from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from threading import Lock
import os

PORT = int(os.environ.get("PORT", 8000))
API_KEY = os.environ.get("API_KEY", "esp8266-key")

app = FastAPI()
templates = Jinja2Templates(directory="templates")
state_lock = Lock()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_THRESHOLD = 20.0


class SensorData(BaseModel):
    temperature: float
    humidity: float
    battery: int

    class Config:
        extra = "ignore"


latest_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "battery": 0,
}

relay_state = False
relay_mode = "AUTO"


@app.post("/data")
def receive_data(data: SensorData, request: Request):
    global latest_data, relay_state

    if request.headers.get("X-API-KEY") != API_KEY:
        return JSONResponse(status_code=403, content={"error": "forbidden"})

    with state_lock:
        latest_data = data.dict()
        if relay_mode == "AUTO":
            relay_state = data.temperature >= TEMP_THRESHOLD

    return {"relay": relay_state, "mode": relay_mode}


@app.get("/api/state")
def api_state():
    return {"data": latest_data, "relay": relay_state, "mode": relay_mode}


@app.post("/relay/on")
def relay_on():
    global relay_state, relay_mode
    with state_lock:
        relay_mode = "MANUAL"
        relay_state = True
    return {"relay": "ON", "mode": relay_mode}


@app.post("/relay/off")
def relay_off():
    global relay_state, relay_mode
    with state_lock:
        relay_mode = "MANUAL"
        relay_state = False
    return {"relay": "OFF", "mode": relay_mode}


@app.post("/relay/auto")
def relay_auto():
    global relay_mode
    with state_lock:
        relay_mode = "AUTO"
    return {"mode": "AUTO"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": latest_data,
            "relay": relay_state,
            "mode": relay_mode,
        },
    )
