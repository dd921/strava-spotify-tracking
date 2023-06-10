import pandas as pd
import plotly.graph_objects as go
import random
from datetime import timedelta
from dateutil import parser


# Read the CSV file into a DataFrame
df = pd.read_csv('~/projects/strava-spotify-tracking/user_data/runs_songs.csv')
# df = pd.read_csv('runs_songs_big.csv')

# Function to generate a random RGB color
def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'


# Datetime Fix
df['song_start_ts'] = df['song_start_ts'].apply(parser.parse)
df['song_end_ts'] = df['song_end_ts'].apply(parser.parse)
df['activity_start_time'] = df['activity_start_time'].apply(parser.parse)

# Sort the dataframe by song_start_ts to ensure proper ordering
df.sort_values('song_start_ts', inplace=True)

# Assign Random RGB Colors for Songs & Activities
df['track_color'] = df['track_name'].apply(lambda x: generate_random_color())
df['activity_color'] = df['activity_name'].apply(lambda x: generate_random_color())

# Create a plotly figure
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
    cum = row['song_length_sec_cum']
    activity_color = row['activity_color']
    proxy_activity_end_ts = row['proxy_activity_end_ts']
    activity_end_ts = row['end_date']
    # Add a line segment for each track
    
    # Plot Activities
    fig.add_trace(go.Scatter(
        x=[activity_start, activity_end_ts], #activity_start + pd.to_timedelta(cum, unit='s')],
        y=[0.1, 0.1],
        mode='lines',
        name=activity_name,
        line=dict(color=activity_color, width=100)
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
    range=[-0.1, 0.2]  # Set the y-axis range
)

# Set figure title
fig.update_layout(
    title='Song End Time Series',
    showlegend=True
)

# Show the plot
fig.show()

