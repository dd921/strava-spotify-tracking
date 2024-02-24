import os
import sys
import json
import time 
import datetime as dt
try:
    import pandas as pd
    import stravalib
    from stravalib.client import Client, model
    from stravalib.exc import RateLimitExceeded
except ImportError:
    print(
        "Some required packages are missing. Please run: pip install -r requirements.txt"
    )
    sys.exit(1)


def get_credentials() -> tuple:
    """Get client ID and client secret from credentials.json or prompt the user to enter them"""
    try:
        with open("credentials.json", "r") as f:
            credentials = json.load(f)
            client_id = credentials["client_id"]
            client_secret = credentials["client_secret"]
    except FileNotFoundError:
        client_id = input("Manually Input your Client ID: ")
        client_secret = input("Manually Input your Client Secret: ")
        with open("credentials.json", "w") as f:
            json.dump({"client_id": client_id, "client_secret": client_secret}, f)
    return client_id, client_secret


def get_authorized_client(
    client_id: str, client_secret: str, redirect_uri: str
) -> Client:
    """Get an authorized client object"""
    client = Client()
    url = client.authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=['read_all','profile:read_all','activity:read_all'],
    )

    print("Authorize the app on: ", url)
    redirected_url = input("Enter Redirect URL: ")

    try:
        code = redirected_url.split("code=")[1].split("&")[0]
        token_response = client.exchange_code_for_token(
            client_id=client_id, client_secret=client_secret, code=code
        )
        client.access_token = token_response["access_token"]

        # access_token = token_response

        # if time.time() > access_token['expires_at']:
        #     print('Token has expired, will refresh')
        #     refresh_response = client.refresh_access_token(client_id=client_id, 
        #                                             client_secret=client_secret, 
        #                                             refresh_token=access_token['refresh_token'])
        #     access_token = refresh_response
        #     # with open('../access_token.pickle', 'wb') as f:
        #     #     pickle.dump(refresh_response, f)
            
        #     with open("access_token.json", "w") as f:
        #         json.dump({"refresh_response": refresh_response}, f)
        #         print('Refreshed token saved to file')

        #     client.access_token = refresh_response['access_token']
        #     client.refresh_token = refresh_response['refresh_token']
        #     client.token_expires_at = refresh_response['expires_at']
        # else:
        #     print('Token still valid, expires at {}'
        #         .format(time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(access_token['expires_at']))))

        #     client.access_token = access_token['access_token']
        #     client.refresh_token = access_token['refresh_token']
        #     client.token_expires_at = access_token['expires_at']

    except IndexError:
        print(
            "Index Error"
        )
        sys.exit(1)

    print("All Done Retrieving Auth")

    return client


def fetch_activities(client: Client) -> pd.DataFrame:
    """Fetch activities from Strava and return a DataFrame"""
    try:
        activities = client.get_activities()
        data = []
        for activity in activities:
            if activity is not None:
                print(activity)
                row = {
                    "id": activity.id,
                    'start_date_local_nzt':activity.start_date_local,
                    "start_date_local": activity.start_date_local.date(),  # yyyy-mm-dd
                    "time_of_day_local": activity.start_date_local.time(),  # hh:mm:ss
                    'elapsed_time': activity.elapsed_time, # seconds
                    "type": activity.sport_type,
                    "distance_mi": activity.distance.num / 1000,  # mi
                    "average_pace_m_s": activity.average_speed,  # m/s
                    "duration": activity.moving_time,  # days hh:mm:ss
                    "altitude_gains_m": activity.total_elevation_gain,  # m
                    "average_heart_rate_bpm": activity.average_heartrate,  # bpm
                    "start_location": activity.start_latlng,  # (lat, lng)
                    "kudos": activity.kudos_count,
                    "temperature_c": None,  # Placeholder
                    "humidity_pct": None,  # Placeholder
                    "air_pressure_hpa": None,  # Placeholder
                }
                data.append(row)
    except RateLimitExceeded:
        print("Rate limit Exceeded")
        sys.exit(1)
    df = pd.DataFrame(data)

    # # Convert all average_pace data to strings and get numeric values
    # df["average_pace_m_s"] = df["average_pace_m_s"].astype(str)
    # df["average_pace_m_s"] = df["average_pace_m_s"].str.split(" ").str[0]
    # df["average_pace_m_s"] = pd.to_numeric(
    #     df["average_pace_m_s"], errors="coerce"
    # ).round(2)


    # Extract numeric altitude gains value and convert to float
    df["altitude_gains_m"] = df["altitude_gains_m"].astype(str)
    df["altitude_gains_m"] = df["altitude_gains_m"].str.split(" ").str[0].astype(float)

    # Reformat location data
    df["start_location"] = df["start_location"].astype(str)
    df["start_location"] = (
        df["start_location"].str.replace("[", "(").str.replace("]", ")")
    )
    df["start_location"] = df["start_location"].str.split("=").str[1]

    # Convert duration from string formatted timedelta to total minutes
    df["duration"] = (df["duration"].dt.total_seconds() / 60).round(2)
    df = df.rename(columns={"duration": "duration_min"})

    # Round distance to 2 decimal places
    # df["distance_km"] = df["distance_km"].round(2)

    return df

def get_hr_stream(activities_df, stream_types: list):
    ''' GET STREAM DATA FOR HEARTRATE ON STRAVA ACTIVITIES'''
    return_stream = []

    for id in activities_df.id:
        try:
            streams = client.get_activity_streams(id, types=stream_types, resolution="medium")
            if streams:
                #  Result is a dictionary object.  The dict's key are the stream type.
                if "time" in streams.keys() and "heartrate" in streams.keys():
                    return_stream.append(
                        {
                            'id': id,
                            'time':streams["time"].data,
                            'heartrate':streams["heartrate"].data
                        }
                    )
                    print(id)
        except:
            pass
        print(return_stream)
    return return_stream


# def fetch_streams(client: Client) -> pd.DataFrame:
#     """Fetch activities from Strava and return a DataFrame"""
#     streams = stravalib.model.Stream
#     print(streams)   

#     return streams

# def getActivityStreams(client, attempts=10):
# 	info = []
# 	for att in attempts:
# 		stream = client.get_activity_streams(att.activity_id, ['altitude','grade_smooth','cadence'])
# 		info.append([str(att.activity_id),
# 					 str(stream['distance'].data).replace(', ','|'),
#                      str(stream['altitude'].data).replace(', ','|')])

# 	return info

if __name__ == "__main__":
    cwd = os.getcwd()
    client_id, client_secret = get_credentials()
    redirect_uri = "http://localhost"
    client = get_authorized_client(client_id, client_secret, redirect_uri)
    df_activities = fetch_activities(client)
    
    # Get heartrate data
    
    df_filtered = df_activities[df_activities['start_date_local'] >= dt.datetime(2024,1,1).date()]
    stream_types = ["time", "heartrate"]
    heartrate = get_hr_stream(df_filtered,stream_types)
    print('make dataframe')
    df_heartrate= pd.DataFrame(heartrate)
    
    df_merged = pd.merge(df_filtered, df_heartrate, on=['id'])

    
    # df_heartrate.to_csv(f"{cwd}/user_data/strava_heartrate.csv", index=False)

    
    # df = getActivityStreams(client)
    df_merged.to_csv("user_data/strava_data_w_heartrate.csv", index=False)

    # Read the data back in and fetch the calories
    df = pd.read_csv("strava_data.csv")
    # df = fetch_calories(client, df)

    # Save all data together
    try:
        df.to_csv("user_data/strava_data.csv", index=False)
    except PermissionError:
        print("Strava Permission Error")
        sys.exit(1)
    # else:
    #     print('error')
