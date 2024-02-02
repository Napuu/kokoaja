from sqlalchemy import create_engine, text, insert
from os import environ
from config import get_db_url, Env
import pandas as pd
import requests
from io import StringIO

engine = create_engine(get_db_url())

def insert_data(table, data):
    with engine.begin() as conn:
        ins_query = insert(table).values(data)
        conn.execute(ins_query)

def get_measurements():
    with engine.begin() as conn:
        return pd.read_sql("select * FROM public.aggregate_5min_view;", conn)

def insert_influx(data: str):
    url = f'{Env.INFLUX_URL}/api/v2/write?org=org1&bucket=rm&precision=s'
    print("INFLUX_URL:", Env.INFLUX_URL)
    headers = {
        'Authorization': f'Token {Env.INFLUX_TOKEN}',
        'Content-Type': 'text/plain'
    }

    response = requests.post(url, headers=headers, data=data)

    print(f'Status Code: {response.status_code}')

def get_measurements_influx():
    headers = {
        'Authorization': f'Token {Env.INFLUX_TOKEN}',
        'Accept': 'application/csv',
        'Content-type': 'application/vnd.flux'
    }

    # Define the Flux query
    query = '''
    from(bucket: "rm")
        |> range(start: -2d)
        |> filter(fn: (r) => r._measurement == "rm" and (r._field == "temperature" or r._field == "humidity" or r._field == "pressure" or r._field == "battery"))
        |> filter(fn: (r) => r.mac == "D26986920F82" or r.mac == "DE8A08E90B9D" or r.mac == "E80742629233")
        |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
        |> yield(name: "5m_averaged_fields")
    '''
    env = Env
    print("INFLUX_URL:, ping", Env.INFLUX_URL, env.INFLUX_URL)
    # Make the request
    response = requests.post(Env.INFLUX_URL, headers=headers, data=query)
    # print(response)
    # Check for errors
    response.raise_for_status()

    # # Parse the response into a Pandas DataFrame
    df = pd.read_csv(StringIO(response.text))  # Skip the first two rows which are headers

    # Show the DataFrame
    df = df[["_time", "_value", "_field", "mac"]].rename(columns={
        "_time": "time",
        "_value": "value",
        "_field": "field",
    })
    df["time"] = pd.to_datetime(df["time"], format="ISO8601")
    df_pivoted = df.pivot_table(index=['time', 'mac'], columns='field', values='value', aggfunc='first')

    df_pivoted.reset_index(inplace=True)

    df_pivoted.columns.name = None  # Removes the 'field' level name

    df_pivoted.columns = [str(col) if not isinstance(col, tuple) else col[1] for col in df_pivoted.columns.values]

    return df_pivoted