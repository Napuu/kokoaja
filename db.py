from sqlalchemy import create_engine, text, insert
from os import environ
from config import get_db_url
import pandas as pd

engine = create_engine(get_db_url())

def insert_data(table, data):
    with engine.begin() as conn:
        ins_query = insert(table).values(data)
        conn.execute(ins_query)

def get_measurements():
    with engine.begin() as conn:
        return pd.read_sql("select * FROM public.aggregate_5min_view;", conn)