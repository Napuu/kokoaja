from os import environ

variables = {
    "DB_URL": "DB_URL",
    "IP_WHITELIST": "IP_WHITELIST",
    "INFLUX_TOKEN": "INFLUX_TOKEN",
    "INFLUX_HOST": "INFLUX_HOST"
}

def check_env_variables() -> list:
    missing = []
    for var in variables.values():
        if var not in environ:
            missing.append(var)
    return missing

def get_ip_whitelist() -> list[str]:
    return environ[variables["IP_WHITELIST"]].split(",")

def get_db_url() -> str:
    return environ[variables["DB_URL"]]

def get_influx_config() -> dict:
    return {
        "INFLUX_TOKEN": environ["INFLUX_TOKEN"],
        "INFLUX_HOST": environ["INFLUX_HOST"]
    }