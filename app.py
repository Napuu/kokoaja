from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from config import check_env_variables, Env
from util import check_ip_is_allowed, generate_graphs
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import logging
import os

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(level=log_level)

if (missing := check_env_variables()) and len(missing) > 0:
    raise Exception(f"Environment variables missing: {', '.join(missing)}")

from db import insert_influx

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/debug", dependencies=[Depends(check_ip_is_allowed)])
async def debug(request: Request):
    print(request.client, request.headers)
    return "hello"

@app.post("/write", dependencies=[Depends(check_ip_is_allowed)])
async def create_measurement(request: Request):
    body = await request.body()
    data = body.decode()

    logging.debug(f"writing following data: {data}")

    insert_influx(data, "rm")

    return {"message": "Measurement recorded successfully"}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/dashboard/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    generate_graphs() 
    # jinja templatea ei oikeastaan ole käytetty tällä hetkellä mihinkään mutta antaa olla
    return templates.TemplateResponse("dashboard.html", {'request':request})