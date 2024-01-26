from datetime import datetime
def parse_telegraf_string(input: str) -> dict:
    table_name, rest = input.split(',', 1)

    columns_with_timestamp = rest.rsplit(' ', 1)
    columns_part = columns_with_timestamp[0]
    timestamp = columns_with_timestamp[1]

    timestamp = datetime.utcfromtimestamp(int(timestamp))

    data = dict(item.split('=') for item in columns_part.replace(' ', ',').split(','))
    data['time'] = timestamp
    return {key.lower(): value for key, value in data.items()}
