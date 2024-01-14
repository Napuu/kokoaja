from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends
from tables import ruuvi_measurement
from config import check_env_variables
from util import check_ip_is_allowed

if (missing := check_env_variables()) and len(missing) > 0:
    raise Exception(f"Environment variables missing: {', '.join(missing)}")

from db import insert_data
from parsers import parse_telegraf_string

app = FastAPI()

@app.get("/debug", dependencies=[Depends(check_ip_is_allowed)])
async def debug(request: Request):
    print(request.client, request.headers)
    return "hello"

@app.post("/telegraf_string/", dependencies=[Depends(check_ip_is_allowed)])
async def create_measurement(request: Request):
    body = await request.body()
    data = body.decode()

    insert_data(ruuvi_measurement, parse_telegraf_string(data))

    return {"message": "Measurement recorded successfully"}
