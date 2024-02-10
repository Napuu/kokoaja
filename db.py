from os import environ
from config import get_db_url, Env
import polars as pl
import requests
from io import StringIO

def insert_influx(data: str):
    url = f'{Env.INFLUX_WRITE_URL}'
    print("INFLUX_READ_URL:", Env.INFLUX_READ_URL)
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

    query = '''
    from(bucket: "rm")
        |> range(start: -2d)
        |> filter(fn: (r) => r._measurement == "rm" and (r._field == "temperature" or r._field == "humidity" or r._field == "pressure" or r._field == "battery"))
        |> filter(fn: (r) => r.mac == "D26986920F82" or r.mac == "DE8A08E90B9D" or r.mac == "E80742629233")
        |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
        |> yield(name: "5m_averaged_fields")
    '''
    response = requests.post(Env.INFLUX_READ_URL, headers=headers, data=query)
    response.raise_for_status()

    df = pl.read_csv(StringIO(response.text))

    df = df.select([
        pl.col("_time").alias("time"),
        pl.col("_value").alias("value"),
        pl.col("_field").alias("field"),
        pl.col("mac")
    ])
    
    df = df.with_columns(pl.col("time").str.strptime(pl.Datetime))

    df_pivoted = df.pivot(index=["time", "mac"], columns="field", values="value")

    return df_pivoted