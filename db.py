from sqlalchemy import create_engine, text, insert
from os import environ
engine = create_engine(environ["DB_URL"])

def insert_data(table, data):
    with engine.begin() as conn:
        ins_query = insert(table).values(data)
        conn.execute(ins_query)