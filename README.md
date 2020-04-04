# twitch-scripts
Abusing the Twitch API.

## Setup
Install Python packages.
```
pip install -r requirements.txt
```

## OAuth
Twitch requires an OAuth token for Helix API access.

- open this [url](https://id.twitch.tv/oauth2/authorize?client_id=msnpl814eots3kcj4yq43yuuojw2zt&redirect_uri=http://localhost&response_type=code) and follow the instructions
- retrieve the authorization code from the url (`code=<code>`)
- execute `python generate_token.py -c <code>` to generate an access token
