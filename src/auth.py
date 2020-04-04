import argparse
import json
import os.path as path
import requests
import sys
import time

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
CLIENT_ID = "msnpl814eots3kcj4yq43yuuojw2zt"
CLIENT_SECRET = "4jo6khpc2ml7ggytl6zu6wao6jhh5w"


def save_token(token):
    token["expires_at"] = time.time() + token["expires_in"]

    with open("token.json", "w") as token_file:
        json.dump(token, token_file, indent=2)

    return token


def load_token():
    if not path.exists("token.json"):
        sys.exit("Token missing")

    with open("token.json", "r") as token_file:
        return json.load(token_file)


class TwitchAuth(requests.auth.AuthBase):
    def __init__(self):
        self.token = load_token()

    def __call__(self, request):
        self.ensure_token()
        request.headers = self.inject(request.headers)

        return request

    def ensure_token(self):
        if self.token["expires_at"] - time.time() > 300:
            return

        response = requests.post(TOKEN_URL, params={
            "grant_type": "refresh_token",
            "client_id": constants.CLIENT_ID,
            "client_secret": constants.CLIENT_SECRET,
            "refresh_token": self.token["refresh_token"]
        })
        if response.status_code == 200:
            self.token = save_token(response.json())
            print("New token :)")
        else:
            sys.exit("Token refresh failed {}".format(response.json()))

    def inject(self, headers):
        headers["Client-ID"] = CLIENT_ID
        headers["Authorization"] = "OAuth {}".format(self.token["access_token"])

        return headers


def fetch_token(code):
    response = requests.post(TOKEN_URL, params={
        "code": code,
        "grant_type": "authorization_code",
        "client_id": constants.CLIENT_ID,
        "client_secret": constants.CLIENT_SECRET,
        "redirect_uri": "http://localhost"
    })
    if response.status_code == 200:
        save_token(response.json())
    else:
        print("Failed authorization", response.json())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", dest="code", type=str, help="authorization code", required=True)

    fetch_token(parser.parse_args().code)
