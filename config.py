from os import environ
from typing import Tuple, Final, NewType
from dataclasses import dataclass

@dataclass
class Env():
    DB_URL = environ["DB_URL"]
    IP_WHITELIST = environ["IP_WHITELIST"]
    INFLUX_TOKEN = environ["INFLUX_TOKEN"]
    INFLUX_URL = environ["INFLUX_URL"]

def check_env_variables() -> list:
    missing = []
    for var in [var for var in vars(Env) if not var.startswith("__")]:
        if var not in environ:
            missing.append(var)
    return missing

def get_ip_whitelist() -> list[str]:
    return Env.IP_WHITELIST.split(",")

def get_db_url() -> str:
    return Env.DB_URL