import pandas as pd
import plotly.graph_objects as go
import random
from datetime import timedelta
from dateutil import parser

from data_cleaning import clean_song_run_data

# Read the CSV file into a DataFrame
df_raw = pd.read_csv('~/projects/strava-spotify-tracking/user_data/runs_songs.csv')

def generate_plot(df):
    fig = go.Figure()

    # Iterate over each track
    for _, row in df.iterrows():
        track_name = row['track_name']
        song_start = row['song_start_ts']
        song_end = row['song_end_ts']
        color = row['track_color']

        # Strava
        activity_name = row['activity_name']
        activity_start = row['activity_start_time']
        activity_color = row['activity_color']
        activity_end_ts = row['end_date']
        # Add a line segment for each track

        # Plot Activities
        fig.add_trace(go.Scatter(
            x=[activity_start, activity_end_ts], #activity_start + pd.to_timedelta(cum, unit='s')],
            y=[0, 0],
            mode='lines',
            name=activity_name,
            line=dict(color=activity_color, width=50),
            legendgroup=True
        ))
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
        range=[df['song_start_ts'].min(), df['song_end_ts'].max()],
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

    # Show the plot
    return fig.show()

def main():
    df = clean_song_run_data(df_raw)
    return generate_plot(df)

if __name__ == '__main__':
    main()


