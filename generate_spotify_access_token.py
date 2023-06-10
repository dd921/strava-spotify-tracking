from urllib.parse import urlencode
from flask import Flask, redirect, request
import requests
import yaml


with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
print(config)
# Access the configuration data
client_id = config['SPOTIFY_API']['client_id']
client_secret = config['SPOTIFY_API']['client_secret']
redirect_uri = config['SPOTIFY_API']['redirect_uri']
scope = config['SPOTIFY_API']['scope'] 

# Spotify API credentials
# client_id = '97c347438bef430f84b20f0571468cc5'
# client_secret = '043fb2da144b494cafbc3008b9934084'
# redirect_uri = 'http://localhost:8000/callback'
# scope = 'user-read-recently-played'

# Flask server setup
app = Flask(__name__)

# Build the authorization URL
authorization_base_url = 'https://accounts.spotify.com/authorize'
authorization_params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scope,
}
authorization_url = authorization_base_url + '?' + urlencode(authorization_params)


@app.route('/')
def index():
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    authorization_code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'

    token_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    token_response = requests.post(token_url, data=token_data)
    access_token = token_response.json()['access_token']

    with open('access_token.txt', 'w') as file:
        file.write(access_token)

    return 'Access Token Generated'

if __name__ == '__main__':
    app.run(port=8000)
