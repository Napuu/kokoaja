from sqlalchemy import create_engine, text, insert
from os import environ
from config import get_db_url
engine = create_engine(get_db_url())

def insert_data(table, data):
    with engine.begin() as conn:
        ins_query = insert(table).values(data)
        conn.execute(ins_query)