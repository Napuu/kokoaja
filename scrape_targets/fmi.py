
import requests
import xml.etree.ElementTree as ET
import datetime
import polars as pl
from datetime import datetime, timedelta
from math import isnan

def get_weather_for_location(location):
    current_time = datetime.utcnow()

    start_time = current_time - timedelta(hours=1)

    timestamp = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    timestamp


    url = ("https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature"
    f"&storedquery_id=fmi::observations::weather::multipointcoverage&place={location}"
    f"&starttime={timestamp}"
    "&timestep=10"
    )

    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)

        ns = {'wfs': 'http://www.opengis.net/wfs/2.0', 
            'gml': 'http://www.opengis.net/gml/3.2',
            'om': 'http://www.opengis.net/om/2.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'gmlcov': 'http://www.opengis.net/gmlcov/1.0',
            'swe': 'http://www.opengis.net/swe/2.0'}

        for member in root.findall('.//wfs:member', ns):
            time = member.find('.//gml:beginPosition', ns)
            temperature = member.find('.//gml:doubleOrNilReasonTupleList', ns)

            if time is not None and temperature is not None:
                rows_as_strings = [row.strip() for row in temperature.text.split("\n") if row.strip()]
                rows_split = [row.split() for row in rows_as_strings]
                measurement_props = [elem.attrib['name'] for elem in root.findall('.//swe:field', ns)]
                timestamps = [row.split()[-1] for row in root.find('.//gmlcov:positions', ns).text.split("\n") if row.strip()]
                rows_final = [dict(zip(measurement_props, row)) for row in rows_split]
                df = pl.DataFrame(rows_final)
                df = df.with_columns(pl.Series(name="timestamp", values=timestamps))
    else:
        print("Failed to fetch data, status code:", response.status_code)

    for column_name in df.columns:
        if column_name == 'timestamp':
            df = df.with_columns(
                df[column_name].cast(pl.Int64)
                .alias(column_name)
            )
        else:
            df = df.with_columns(
                df[column_name].cast(pl.Float32, strict=False)
                .alias(column_name)
            )
    return df