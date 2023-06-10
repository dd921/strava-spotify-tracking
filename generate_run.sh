#!/bin/bash

# Run Python scripts sequentially
# python get_spotify_access_token.py &
# python get_spotify_data.py &
# python get_strava_data.py
python combine_songs_and_activity_data.py
# python plot_songs_and_activities.py &


# lsof -i :5000