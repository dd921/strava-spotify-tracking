import requests
import pandas as pd
import sys


def process_recently_played(access_token):
    # Get recently played tracks
    recently_played_url = 'https://api.spotify.com/v1/me/player/recently-played'
    recently_played_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    recently_played_params = {
        'limit': 50,  # Maximum number of tracks to retrieve (adjust as needed)
    }

    recently_played_response = requests.get(recently_played_url, params=recently_played_params, headers=recently_played_headers)
    recently_played_data = recently_played_response.json()

    print("Status Code:", recently_played_response.status_code)
    print("Response Text:", recently_played_response.text)
    # Process recently played tracks
    if 'items' in recently_played_data:
        tracks = []
        for item in recently_played_data['items']:
            track_name = item['track']['name']
            artist_name = item['track']['artists'][0]['name']
            played_at = item['played_at']
            duration_ms = item['track']['duration_ms']
            duration_s = item['track']['duration_ms']*1000
            tracks.append({'Track Name': track_name,
                           'Artist Name': artist_name,
                           'Played At': played_at,
                           'duration_ms': duration_ms,
                           'duration_ms': duration_s,
                           })
        df = pd.DataFrame(tracks)
        df = df.rename(columns={
        'Track Name': 'track_name',
        'Artist Name': 'artist',
        'Played At': 'song_start_ts_utc',
        })
        df.sort_values(by=['song_start_ts_utc'], inplace=True)  # Corrected line
        return df
    else:
        print('No recently played tracks found')
        print(recently_played_data)
        return None

# Read the access token generated in generate_spotify_access_token.py
with open('/Users/dandeangelis/projects/strava-spotify-tracking/access_tokens/access_token.txt', 'r') as file:
    access_token = file.read().strip()

# Call the process_recently_played function with the access token
df = process_recently_played(access_token)
print(df)
# Save DataFrame to a CSV file
if df is not None:
    df.to_csv('user_data/recently_played.csv',  mode='a', header=False, index=False)
    print('Recently played tracks saved successfully')
    sys.exit(0)
