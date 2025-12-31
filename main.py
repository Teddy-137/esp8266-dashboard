from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os

PORT = int(os.environ.get("PORT", 8000))

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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


latest_data = {
    "temperature": 0.0,
    "humidity": 0.0,
    "battery": 0,
}

# Relay control
relay_state = False  # actual relay output
relay_mode = "AUTO"  # AUTO or MANUAL


@app.post("/data")
def receive_data(data: SensorData):
    global latest_data, relay_state

    latest_data = data.dict()

    # AUTO mode → server decides relay
    if relay_mode == "AUTO":
        relay_state = data.temperature >= TEMP_THRESHOLD

    return {"status": "ok", "relay": relay_state, "mode": relay_mode}


@app.get("/api/state")
def api_state():
    return {"data": latest_data, "relay": relay_state, "mode": relay_mode}


@app.post("/relay/on")
def relay_on():
    global relay_state, relay_mode
    relay_mode = "MANUAL"
    relay_state = True
    return {"relay": "ON", "mode": relay_mode}


@app.post("/relay/off")
def relay_off():
    global relay_state, relay_mode
    relay_mode = "MANUAL"
    relay_state = False
    return {"relay": "OFF", "mode": relay_mode}


@app.post("/relay/auto")
def relay_auto():
    global relay_mode
    relay_mode = "AUTO"
    return {"mode": "AUTO"}


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
