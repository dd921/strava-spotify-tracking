import pandas as pd
import plotly.graph_objects as go
import random
from datetime import timedelta
from dateutil import parser

def clean_song_run_data(df):
    # Datetime Fix
    df['song_start_ts'] = df['song_start_ts'].apply(parser.parse)
    df['song_end_ts'] = df['song_end_ts'].apply(parser.parse)
    df['activity_start_time'] = df['activity_start_time'].apply(parser.parse)

    # Sort the dataframe by song_start_ts to ensure proper ordering
    df.sort_values('song_start_ts', inplace=True)

    # Assign Random RGB Colors for Songs & Activities
    df['track_color'] = df['track_name'].apply(lambda x: generate_random_color())
    df['activity_color'] = df['activity_name'].apply(lambda x: generate_random_color())
    return df

# Function to generate a random RGB color
def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'
