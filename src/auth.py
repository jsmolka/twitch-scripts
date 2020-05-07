import json
import os.path as path
import requests
from time import time
from datetime import datetime
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import urlencode
from urllib.parse import urlparse

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
CLIENT_ID = "msnpl814eots3kcj4yq43yuuojw2zt"
CLIENT_SECRET = "4jo6khpc2ml7ggytl6zu6wao6jhh5w"


def save_token(token):
    token["expires_at"] = time() + token["expires_in"]

    with open("token.json", "w") as token_file:
        json.dump(token, token_file, indent=2)

    return token


def load_token():
    if not path.exists("token.json"):
        exit("Token missing")

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
        if self.token["expires_at"] - time() > 300:
            return

        response = requests.post(TOKEN_URL, params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": self.token["refresh_token"]
        })
        if response.status_code == 200:
            self.token = save_token(response.json())
        else:
            print(datetime.now(), "Token refresh failed {}".format(response.json()))

    def inject(self, headers):
        headers["Client-ID"] = CLIENT_ID
        headers["Authorization"] = "OAuth {}".format(self.token["access_token"])

        return headers


def fetch_token(code):
    response = requests.post(TOKEN_URL, params={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost"
    })
    if response.status_code == 200:
        save_token(response.json())
    else:
        print(datetime.now(), "Authorization failed", response.json())


def auth():
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "channel_editor",
        "redirect_uri": "http://localhost"
    }, quote_via=quote)

    print("Paste this url into a browser and follow the instructions:")
    print("https://id.twitch.tv/oauth2/authorize?{}".format(query))

    parse = urlparse(input("Paste the result: "))
    query = parse_qs(parse.query)
    if "code" not in query:
        exit("Invalid result")

    fetch_token(query["code"])


if __name__ == "__main__":
    auth()
