import requests
import pandas as pd
import yaml
import os
# Load configuration from YAML file
with open('~/strava-spotify-tracking/access_tokens/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

client_id = config['STRAVA_API']['client_id']
client_secret = config['STRAVA_API']['client_secret']
redirect_uri = config['STRAVA_API']['redirect_uri']

# Obtain authorization code from Strava (user interaction required)
authorize_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=read_all,activity:read_all"
print(f"Please visit this URL and authorize the app:\n{authorize_url}")
authorization_code = input("Enter the authorization code: ")

# Exchange authorization code for access token
token_endpoint = 'https://www.strava.com/oauth/token'
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'code': authorization_code,
    'grant_type': 'authorization_code'
}
response = requests.post(token_endpoint, data=payload)
access_token = response.json()['access_token']

# Fetch activities using the access token
activities_endpoint = 'https://www.strava.com/api/v3/athlete/activities'
headers = {'Authorization': 'Bearer ' + access_token}
response = requests.get(activities_endpoint, headers=headers)
activities = response.json()

# Create DataFrame, handle existing IDs
existing_ids = []
if os.path.exists('user_data/strava_activities.csv'):
    df_existing = pd.read_csv('user_data/strava_activities.csv')
    existing_ids = df_existing['id'].tolist()

new_activities = [activity for activity in activities if activity['id'] not in existing_ids]

# Only process and save new activities
if new_activities:
    df_activities = pd.DataFrame(new_activities)
    df_activities['end_date'] = pd.to_datetime(df_activities['start_date']) + pd.to_timedelta(df_activities['elapsed_time'], unit='s')

    # Append data to existing file with "a" mode (append)
    df_activities.to_csv('user_data/strava_activities.csv', index=False, mode='a', header=False)

    print("New activities saved to strava_activities.csv")
else:
    print("No new activities found.")
