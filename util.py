from fastapi import HTTPException, Request
import pytz
import time
import functools
import matplotlib.ticker as mticker
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import polars as pl
import locale
from math import isnan
from db import get_measurements_influx

from config import get_ip_whitelist


async def check_ip_is_allowed(request: Request):
    allowed_ips = get_ip_whitelist()
    client_ip = request.headers.get('x-real-ip', request.client.host)
    if client_ip not in allowed_ips:
        raise HTTPException(status_code=403, detail="🗿")

def debounce(interval):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, '_last_call'):
                wrapper._last_call = 0

            now = time.time()
            if now - wrapper._last_call >= interval:
                wrapper._last_call = now
                return func(*args, **kwargs)

        return wrapper
    return decorator

def plot_combined_data(grouped, mac_addresses, measurement, plot_title, y_label, file_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Loop through each room's MAC address
    for mac, label in mac_addresses.items():
        df = grouped.filter(pl.col('mac') == mac)
        ax.plot(df['time'], df[measurement], linestyle='-', markersize=2, label=label)

    # Setting labels and title
    ax.set_title(plot_title)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M', tz=pytz.timezone('EET')))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x}{y_label}'))

    # Set dynamic y-axis limits
    overall_min = grouped[measurement].min()
    overall_max = grouped[measurement].max()
    overall_range = overall_max - overall_min
    ax.set_ylim(overall_min - overall_range * 0.2, overall_max + overall_range * 0.3)

    ax.grid(True)
    ax.legend()
    fig.autofmt_xdate()
    plt.savefig(file_name, format='png', dpi=300)
    plt.close(fig)

@debounce(60)
def generate_graphs():
    print("generating graphs")
    room_data = {
        "D26986920F82": "Olohuone",
        "DE8A08E90B9D": "Kylpyhuone",
        "E80742629233": "Makuuhuone"
    }
    locale.setlocale(locale.LC_TIME, 'fi_FI.utf-8')
    measurements = get_measurements_influx()

    plot_combined_data(measurements, room_data, 'temperature', 'Lämpötila sisällä', '°C', 'static/temperature_combined.png')

    plot_combined_data(measurements, room_data, 'humidity', 'Kosteus sisällä', '%', 'static/humidity_combined.png')

def df_to_influx_line_protocol(df, bucket, **tags):
    def is_numeric_property(row, key):
        return key != 'timestamp' and not isnan(row[key])
    def is_non_null_row(row):
        return any(row[key] for key in row.keys() if is_numeric_property(row, key))
    def parse_tags(**tags):
        return ",".join([f"{key}={value}" for key, value in tags.items()])
    return [
        f"{bucket}{',' if len(tags) > 0 else ''}{parse_tags(**tags)} " +
        ",".join([f"{key}={row[key]}" for key in row.keys() if is_numeric_property(row, key)]) +
        f" {row['timestamp']}"
        for row in df.to_dicts()
        if is_non_null_row(row)
    ]
    return lines