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
from db import get_measurements

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

@debounce(60)
def generate_graphs():
    print("generating graphs")
    olohuone = "D26986920F82"
    kylpyhuone = "DE8A08E90B9D"
    makuuhuone = "E80742629233"
    locale.setlocale(locale.LC_TIME, 'fi_FI.utf-8')
    measurements = get_measurements()

    grouped = measurements.groupby(by='mac')

    window_size = 2


    # kylpyhuone kosteus
    fig = plt.Figure()
    df = grouped.get_group(kylpyhuone).copy()
    df['avg_humidity_smoothed'] = df['avg_humidity'].rolling(window=window_size).mean()

    plt.figure(figsize=(10, 6))
    plt.title('Kosteus - kylpyhuone')
    plt.plot(df['time_interval'], df['avg_humidity_smoothed'], linestyle='-', markersize=2)
    plt.ylim(20, 80)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M', tz=pytz.timezone('EET')))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter())

    plt.grid(True)

    plt.gcf().autofmt_xdate()
    plt.savefig('static/humidity_kylpyhuone.png', format='png', dpi=300)

    # kylpyhuone lämpötila
    fig = plt.Figure()
    df['avg_temperature_smoothed'] = df['avg_temperature'].rolling(window=window_size).mean()

    plt.figure(figsize=(10, 6))
    plt.title('Lämpötila - kylpyhuone')
    plt.plot(df['time_interval'], df['avg_temperature_smoothed'], linestyle='-', markersize=2)
    plt.ylim(16, 26)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x}°C'))

    plt.grid(True)

    plt.gcf().autofmt_xdate()
    plt.savefig('static/temperature_kylpyhuone.png', format='png', dpi=300)


    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting for 'olohuone'
    df = grouped.get_group(olohuone).copy()
    df['avg_temperature_smoothed'] = df['avg_temperature'].rolling(window=window_size).mean()
    l1, = ax.plot(df['time_interval'], df['avg_temperature_smoothed'], linestyle='-', markersize=2, label='Olohuone')

    # Plotting for 'kylpyhuone'
    df = grouped.get_group(kylpyhuone).copy()
    df['avg_temperature_smoothed'] = df['avg_temperature'].rolling(window=window_size).mean()
    l2, = ax.plot(df['time_interval'], df['avg_temperature_smoothed'], linestyle='-', markersize=2, label='Kylpyhuone')

    # Plotting for 'makuuhuone'
    df = grouped.get_group(makuuhuone).copy()
    df['avg_temperature_smoothed'] = df['avg_temperature'].rolling(window=window_size).mean()
    l3, = ax.plot(df['time_interval'], df['avg_temperature_smoothed'], linestyle='-', markersize=2, label='Makuuhuone')

    # Setting labels and title
    ax.set_title('Lämpötila sisällä')

    # Formatting axes
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M', tz=pytz.timezone('EET')))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x}°C'))
    ax.set_ylim(16, 26)

    # Adding grid and legend
    ax.grid(True)
    ax.legend()

    # Auto-format for date display
    fig.autofmt_xdate()
    # plt.gcf().autofmt_xdate()

    plt.grid(True)

    plt.savefig('static/temperature_olohuone.png', format='png', dpi=300)
    
    # olohuone kosteus
    fig = plt.Figure()
    df['avg_humidity_smoothed'] = df['avg_humidity'].rolling(window=window_size).mean()

    plt.figure(figsize=(10, 6))
    plt.title('Kosteus - olohuone')
    plt.plot(df['time_interval'], df['avg_humidity_smoothed'], linestyle='-', markersize=2)
    plt.ylim(20, 80)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter())

    plt.grid(True)

    plt.gcf().autofmt_xdate()
    plt.savefig('static/humidity_olohuone.png', format='png', dpi=300)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting for 'olohuone'
    df = grouped.get_group(olohuone).copy()
    df['avg_humidity_smoothed'] = df['avg_humidity'].rolling(window=window_size).mean()
    l1, = ax.plot(df['time_interval'], df['avg_humidity_smoothed'], linestyle='-', markersize=2, label='Olohuone')

    # Plotting for 'kylpyhuone'
    df = grouped.get_group(kylpyhuone).copy()
    df['avg_humidity_smoothed'] = df['avg_humidity'].rolling(window=window_size).mean()
    l2, = ax.plot(df['time_interval'], df['avg_humidity_smoothed'], linestyle='-', markersize=2, label='Kylpyhuone')

    # Plotting for 'makuuhuone'
    df = grouped.get_group(makuuhuone).copy()
    df['avg_humidity_smoothed'] = df['avg_humidity'].rolling(window=window_size).mean()
    l3, = ax.plot(df['time_interval'], df['avg_humidity_smoothed'], linestyle='-', markersize=2, label='Makuuhuone')

    # Setting labels and title
    ax.set_title('Kosteus sisällä')

    # Formatting axes
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M', tz=pytz.timezone('EET')))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x}%'))
    ax.set_ylim(20, 80)

    # Adding grid and legend
    ax.grid(True)
    ax.legend()

    # Auto-format for date display
    fig.autofmt_xdate()
    # plt.gcf().autofmt_xdate()

    plt.grid(True)

    plt.savefig('static/humidity_olohuone.png', format='png', dpi=300)