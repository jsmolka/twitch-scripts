import auth
import requests

API_URL = "https://api.twitch.tv"
TWITCH_AUTH = auth.TwitchAuth()


def error(response):
    lines = [
        "Bad response:",
        response.url,
        response.text
    ]
    raise RuntimeError("\n".join(lines))


def get(url, **kwargs):
    response = requests.get(url, **kwargs, auth=TWITCH_AUTH, timeout=60)

    if response.status_code != 200:
        error(response)

    return response


def base(url, **kwargs):
    return get("{}/{}".format(API_URL, url), **kwargs)


def json(url, **kwargs):
    return base(url, **kwargs).json()
