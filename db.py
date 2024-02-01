from sqlalchemy import create_engine, text, insert
from os import environ
import requests
from config import get_db_url, get_influx_config, variables
import pandas as pd

engine = create_engine(get_db_url())

def insert_data(table, data):
    with engine.begin() as conn:
        ins_query = insert(table).values(data)
        conn.execute(ins_query)

def get_measurements():
    with engine.begin() as conn:
        return pd.read_sql("select * FROM public.aggregate_5min_view;", conn)

def insert_influx(data: str):
    influx_config = get_influx_config()
    url = f'{influx_config["INFLUX_HOST"]}/api/v2/write?org=org1&bucket=rm&precision=s'
    headers = {
        'Authorization': f'Token {influx_config["INFLUX_TOKEN"]}',
        'Content-Type': 'text/plain'
    }

    response = requests.post(url, headers=headers, data=data)
