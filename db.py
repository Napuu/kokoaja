from os import environ
from config import get_db_url, Env
import pandas as pd
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
    env = Env
    print("INFLUX_READ_URL:, ping", Env.INFLUX_READ_URL, env.INFLUX_READ_URL)
    response = requests.post(Env.INFLUX_READ_URL, headers=headers, data=query)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))  # Skip the first two rows which are headers

    df = df[["_time", "_value", "_field", "mac"]].rename(columns={
        "_time": "time",
        "_value": "value",
        "_field": "field",
    })
    df["time"] = pd.to_datetime(df["time"], format="ISO8601")
    df_pivoted = df.pivot_table(index=['time', 'mac'], columns='field', values='value', aggfunc='first')

    df_pivoted.reset_index(inplace=True)

    df_pivoted.columns.name = None

    df_pivoted.columns = [str(col) if not isinstance(col, tuple) else col[1] for col in df_pivoted.columns.values]

    return df_pivoted