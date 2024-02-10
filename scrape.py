import argparse
from scrape_targets import fmi
from util import df_to_influx_line_protocol
from db import insert_influx

def main():
    parser = argparse.ArgumentParser(description='Run the scraper on a given target.')
    parser.add_argument('target')
    args = parser.parse_args()
    
    target = args.target
    if target == "fmi":
        location = "kupittaa"
        bucket = "weather"
        res = fmi.get_weather_for_location(location)
        rows = df_to_influx_line_protocol(res, bucket, location=location)
        for row in rows:
            insert_influx(row)
    
if __name__ == '__main__':
    main()