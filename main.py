from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from threading import Lock

from mqtt_client import (
    client,
    latest_data,
    relay_state,
    device_status,
    state_lock,
    TOPIC_RELAY,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("static/manifest.json", media_type="application/json")


@app.get("/sw.js")
async def get_sw():
    return FileResponse("static/sw.js", media_type="application/javascript")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_THRESHOLD = 7.0
relay_mode = "AUTO"  # AUTO | MANUAL

# ================= RELAY CONTROL =================


@app.post("/relay/on")
def relay_on():
    global relay_mode, relay_state

    with state_lock:
        relay_mode = "MANUAL"
        relay_state = True
        client.publish(TOPIC_RELAY, "ON")

    return {"relay": "ON", "mode": relay_mode}


@app.post("/relay/off")
def relay_off():
    global relay_mode, relay_state

    with state_lock:
        relay_mode = "MANUAL"
        relay_state = False
        client.publish(TOPIC_RELAY, "OFF")

    return {"relay": "OFF", "mode": relay_mode}


@app.post("/relay/auto")
def relay_auto():
    global relay_mode
    relay_mode = "AUTO"
    return {"mode": "AUTO"}


# ================= AUTO CONTROL LOOP =================


@app.get("/control/auto")
def auto_control():
    global relay_state

    with state_lock:
        if relay_mode == "AUTO":
            relay_state = latest_data["temperature"] >= TEMP_THRESHOLD
            client.publish(TOPIC_RELAY, "ON" if relay_state else "OFF")

    return {"relay": relay_state, "mode": relay_mode}


# ================= API =================


@app.get("/api/state")
def api_state():
    return {
        "data": latest_data,
        "relay": relay_state,
        "mode": relay_mode,
        "device": device_status,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ================= DASHBOARD =================


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": latest_data,
            "relay": relay_state,
            "mode": relay_mode,
            "device": device_status,
        },
    )
