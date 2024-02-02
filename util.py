from fastapi import HTTPException, Request
import pytz
import time
import functools
import matplotlib.ticker as mticker
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import locale
from db import get_measurements, get_measurements_influx

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

def plot_combined_data(grouped, mac_addresses, measurement, window_size, plot_title, y_label, file_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Loop through each room's MAC address
    for mac, label in mac_addresses.items():
        df = grouped.get_group(mac).copy()
        ax.plot(df['time'], df[measurement], linestyle='-', markersize=2, label=label)

    # Setting labels and title
    ax.set_title(plot_title)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M', tz=pytz.timezone('EET')))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x}{y_label}'))

    # Set dynamic y-axis limits
    overall_min = grouped[measurement].min().min()
    overall_max = grouped[measurement].max().max()
    overall_range = overall_max - overall_min
    ax.set_ylim(overall_min - overall_range * 0.2, overall_max + overall_range * 0.3)

    ax.grid(True)
    ax.legend()
    fig.autofmt_xdate()
    plt.savefig(file_name, format='png', dpi=300)

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
    print(measurements)

    print(get_measurements_influx())

    grouped = measurements.groupby(by='mac')
    window_size = 2

    plot_combined_data(grouped, room_data, 'temperature', window_size, 'Lämpötila sisällä', '°C', 'static/temperature_combined.png')

    plot_combined_data(grouped, room_data, 'humidity', window_size, 'Kosteus sisällä', '%', 'static/humidity_combined.png')

