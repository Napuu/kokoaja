from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from tables import ruuvi_measurement

from db import insert_data
from parsers import parse_telegraf_string

app = FastAPI()

@app.post("/telegraf_string/")
async def create_measurement(request: Request):
    body = await request.body()
    data = body.decode()

    insert_data(ruuvi_measurement, parse_telegraf_string(data))

    return {"message": "Measurement recorded successfully"}
