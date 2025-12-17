from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class SensorData(BaseModel):
    temperature: float
    humidity: float
    battery: int


latest_data = {"temperature": 0, "humidity": 0, "battery": 0}

relay_state = False


@app.post("/data")
def receive_data(data: SensorData):
    global latest_data
    latest_data = data.dict()
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "data": latest_data, "relay": relay_state},
    )


@app.get("/relay")
def get_relay_state():
    return {"relay": relay_state}


@app.post("/relay/on")
def relay_on():
    global relay_state
    relay_state = True
    return {"relay": "ON"}


@app.post("/relay/off")
def relay_off():
    global relay_state
    relay_state = False
    return {"relay": "OFF"}


@app.get("/api/battery")
def battery_history():
    return {"history": list(battery_deque)}
