import argparse
import constants
import json
import requests

from datetime import datetime
from datetime import timedelta


def save_token(response):
    data = {
        "access_token": response.get("access_token", ""),
        "refresh_token": response.get("refresh_token", ""),
        "expiry_date": str(datetime.now() + timedelta(seconds=response.get("expires_in", 0)))
    }
    with open("token.json", "w") as token_file:
        json.dump(data, token_file, indent=2)


def generate_token(code):
    params = {
        "code": code,
        "client_id": constants.CLIENT_ID,
        "client_secret": constants.CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost"
    }
    response = requests.post("https://id.twitch.tv/oauth2/token", params=params)
    if response.status_code == 200:
        save_token(response.json())
    else:
        print("Something went wrong", response.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", dest="code", type=str, help="authorization code", required=True)

    generate_token(parser.parse_args().code)
