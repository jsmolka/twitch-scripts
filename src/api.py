import ssl
import requests

API_BASE = "https://api.twitch.tv"
CLIENT_ID = "msnpl814eots3kcj4yq43yuuojw2zt"


def _inject_headers(**kwargs):
    if "headers" not in kwargs:
        kwargs["headers"] = {}

    kwargs["headers"]["Client-ID"] = CLIENT_ID
    kwargs["headers"]["Accept"] = "application/vnd.twitchtv.v5+json"

    return kwargs


def _handle_error(response):
    lines = [
        "Bad response:",
        response.url,
        response.text
    ]
    raise RuntimeError("\n".join(lines))


def get(url, **kwargs):
    response = requests.get(url, **_inject_headers(**kwargs), timeout=60)

    if response.status_code != 200:
        _handle_error(response)

    return response


def get_base(path, **kwargs):
    return get("{}/{}".format(API_BASE, path), **kwargs)


def get_json(path, **kwargs):
    return get_base(path, **kwargs).json()
