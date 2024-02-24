import pandas as pd
import plotly.graph_objects as go
import random
from datetime import timedelta
from dateutil import parser
import pytz 
from strava_spotify.data_cleaning import clean_song_run_data

# Read the CSV file into a DataFrame
# df_raw = pd.read_csv('~/projects/strava-spotify-tracking/user_data/runs_songs.csv')


def generate_plot(df, df_activities):
    fig = go.Figure()
    print(df_activities.columns)

    # Sort the dataframe by song_start_ts to ensure proper ordering
    df.sort_values('timestamp_est', inplace=True)

    # Assign Random RGB Colors for Songs & Activities
    df['track_color'] = df['track_name'].apply(lambda x: generate_random_color())
    df_activities['activity_color'] = df_activities['name'].apply(lambda x: generate_random_color())


    for _, row in df_activities.iterrows():
            # # Strava
        activity_name = row['name']
        activity_start = row['start_date_local']
        activity_color = row['activity_color']
        activity_end_ts = row['end_date']
        # Add a line segment for each track
        # Plot Activities
        print(row)
        fig.add_trace(go.Scatter(
            x=[activity_start, activity_end_ts], #activity_start + pd.to_timedelta(cum, unit='s')],
            y=[3, 3],
            mode='lines',
            name=activity_name,
            line=dict(color='red', width=200),
            legendgroup=True
        ))

    # Iterate over each track
    for _, row in df.iterrows():
        track_name = row['track_name']
        song_start = row['timestamp_est']
        song_end = row['song_end_ts']
        color = row['track_color']
   
        x_values = [song_start, song_end]
        print(x_values)

        # Plot Activities
        # fig.add_trace(go.Scatter(
        #     x=[activity_start, activity_end_ts], #activity_start + pd.to_timedelta(cum, unit='s')],
        #     y=[0, 0],
        #     mode='lines',
        #     name=activity_name,
        #     line=dict(color=activity_color, width=50),
        #     legendgroup=True
        # ))
        # Plot Songs
        fig.add_trace(go.Scatter(
            x=[song_start, song_end],
            y=[0, 0],
            mode='lines',
            name=track_name,
            line=dict(color=color, width=100)
        ))

    # Set the layout properties
    fig.update_layout(
        title="Track Timeline",
        xaxis=dict(title="Time"),
        yaxis=dict(title="Track Name"),
    )
    # Set x-axis and y-axis properties
    fig.update_xaxes(
        title='Time',
        type='date',
        range=[df['timestamp_est'].min(), df['song_end_ts'].max()],
    )
    fig.update_yaxes(
        title='Value',
        range=[-0.1, 0.1]  # Set the y-axis range
    )

    # Set figure title
    fig.update_layout(
        title='Spotify Songs vs Strava Activities',
        showlegend=True
    )

    fig.update_xaxes(range=[min(x_values), max(x_values)])

    # Show the plot
    return fig.show()

# Function to generate a random RGB color
def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'


def main():
    
    df_songs = pd.read_csv("~/strava-spotify-tracking/user_data/recently_played.csv")
    df_activity = pd.read_csv("~/strava-spotify-tracking/hr_activities.csv")
    df_songs['Played At'] = pd.to_datetime(df_songs['Played At'])

    # Function to convert UTC to EST
    def convert_utc_to_est(utc_time):
        utc_time = utc_time.replace(tzinfo=pytz.utc)  # Ensure UTC timezone
        est_time = utc_time.astimezone(pytz.timezone('US/Eastern'))  # Convert to EST
        return est_time

    # Apply the function to the 'timestamp_utc' column
    df_songs['timestamp_est'] = df_songs['Played At'].apply(convert_utc_to_est)
    
    df_songs['song_end_ts'] = df_songs['timestamp_est'] + pd.to_timedelta(df_songs['duration_ms']/1000, unit='ms')
    df_songs['song_length'] = df_songs['song_end_ts'] - df_songs['timestamp_est']

    # Convert to Minutes  and round
    df_songs['song_length_min']  = df_songs['song_length'].dt.total_seconds()/60
    df_songs['song_length_min'] = df_songs['song_length_min'].round(5)   
    
    # Rename Columns:
    df_songs = df_songs.rename(columns={
        'Track Name': 'track_name',
        'Artist Name': 'artist',
        'Played At': 'song_start_ts_utc',
    })



    # df = clean_song_run_data(df_songs)
    return generate_plot(df_songs, df_activity[df_activity.id == 10634057895])

if __name__ == '__main__':
    

    main()
