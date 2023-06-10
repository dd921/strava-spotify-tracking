from flask import Flask, request, redirect
import requests
import json
import pandas as pd
import yaml
from dateutil import parser

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Access the configuration data
client_id = config['STRAVA_API']['client_id']
client_secret = config['STRAVA_API']['client_secret']
redirect_uri = config['STRAVA_API']['redirect_uri']

app = Flask(__name__)

@app.route('/')
def index():
    # Redirect the user to the Strava authorization endpoint
    authorize_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=read_all,activity:read_all"
    return redirect(authorize_url)

@app.route('/callback')
def callback():
    # Retrieve the authorization code from the query parameters
    code = request.args.get('code')

    # Exchange the authorization code for an access token
    token_endpoint = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(token_endpoint, data=payload)
    response_data = response.json()
    access_token = response_data['access_token']

    # Use the access token to fetch activities
    activities_endpoint = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(activities_endpoint, headers=headers)
    activities = json.loads(response.text)
    df_activities = pd.DataFrame(activities)

    # Add an end_time for the activity by adding start_time and elapsed time
    df_activities['end_date'] = pd.to_datetime(df_activities['start_date']) + pd.to_timedelta(df_activities['elapsed_time'], unit='s')

    # Save strava activities to CSV
    df_activities.to_csv('strava_activities.csv', index=False)

    return df_activities # consider commenting this out

if __name__ == '__main__':
    app.run()
