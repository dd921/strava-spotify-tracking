import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from datetime import timedelta

# Read the CSV files into pandas DataFrames
songs_df = pd.read_csv('recently_played.csv')
activities_df = pd.read_csv('strava_activities.csv')


songs_df = songs_df.rename(columns={'Track Name': 'track_name',
                                    'Artist Name': 'artist_name',
                                    'Played At': 'played_at',
                                    'duration_ms': 'duration_ms'})

activities_df = activities_df.rename(columns={'elapsed_time': 'duration',
                                              'workout_type': 'activity_type',
                                              'id': 'activity_id',
                                              'name': 'activity_name',
                                              'distance': 'distance_km',
                                              'moving_time': 'moving_time',
                                              'location_state': 'location',
                                              'average_speed': 'average_speed_km/h',
                                              'average_heartrate': 'average_heart_rate',
                                              'max_heartrate': 'max_heart_rate',
                                              'max_speed': 'max_speed_km/h'})

def expand_dataframe(df):
    expanded_rows = []
    df['timeline'] = df['song_start_ts']
    for index, row in df.iterrows():
        start_ts = row['song_start_ts']
        end_ts = row['song_end_ts']
        duration_sec = row['song_length_sec']
        
        while start_ts < end_ts:
            new_row = row.copy()
            new_row['timeline'] = start_ts
            new_row['song_length_sec'] = 1
            
            expanded_rows.append(new_row)
            
            start_ts += timedelta(seconds=1)
            duration_sec -= 1
            
        # Update the last row with the remaining duration
        expanded_rows[-1]['song_length_sec'] = duration_sec
    
    expanded_df = pd.DataFrame(expanded_rows)
    
    return expanded_df

def join_and_return(df1, df2, join_columns, return_columns):
    """
    Function to join two dataframes on specified columns and return a new dataframe with selected columns.
    
    Args:
        df1 (pandas.DataFrame): First dataframe.
        df2 (pandas.DataFrame): Second dataframe.
        join_columns (list): List of column names to join on for both dataframes.
        return_columns (list): List of column names to return in the final dataframe.
        
    Returns:
        pandas.DataFrame: New dataframe with selected columns after joining.
    """
    # Perform the join operation on specified columns
    merged_df = pd.merge(df1, df2, on=join_columns)
    # print(merged_df.columns)
    # Select the desired columns
    selected_columns = merged_df[return_columns]
    
    return selected_columns


def add_truncated_date_columns(df):
    """
    Function to add truncated date columns for datetime columns in a dataframe.
    
    Args:
        df (pandas.DataFrame): Input dataframe.
        
    Returns:
        pandas.DataFrame: Updated dataframe with truncated date columns.
    """
    # Iterate over the columns
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            # Add a truncated date column with the original name + "_trunc"
            trunc_column = column + "_trunc"
            df[trunc_column] = df[column].dt.strftime('%Y-%m-%d')

    return df

# print(songs_df.columns)
# Convert the timestamp columns to datetime objects
songs_df['played_at'] = pd.to_datetime(songs_df['played_at'])
# Track Name, Artist Name, Played At

# elapsed_time, workout_type, id, name, distance, moving_time, location_state, average_speed, average_heartrate, max_heartrate, max_speed
activities_df['start_date'] = pd.to_datetime(activities_df['start_date'])

# # Sort both DataFrames based on the 'start_time' column
songs_df = songs_df.sort_values('played_at')
activities_df = activities_df.sort_values('start_date')

# Create an empty list to store the closest song timestamps for each activity
closest_song_times = []
durations = []
activity_names = []
# Iterate over the activities DataFrame and find the closest song timestamp for each activity start time
for _, activity_row in activities_df.iterrows():
    # print(activity_row)
    activity_time = activity_row['start_date']
    activity_name = activity_row['activity_name']
    closest_song_time = songs_df['played_at'].min()  # Find the minimum song timestamp
    duration = songs_df['duration_ms'].loc[songs_df['played_at'] == closest_song_time]
    for song_time in songs_df['played_at']:
        if abs(song_time - activity_time) < abs(closest_song_time - activity_time):
            closest_song_time = song_time
    closest_song_times.append(closest_song_time)
    durations.append(duration)
    activity_names.append(activity_name)

# Create a new DataFrame using the closest song timestamps
new_df = pd.DataFrame({'activity_start_time': activities_df['start_date'],
                        'end_date': activities_df['end_date'],
                       'activity_name': activity_names,
                       'closest_song_time': closest_song_times,
                       'duration': durations
                       })

new_df['played_at'] = new_df['closest_song_time']
new_df = add_truncated_date_columns(new_df)
songs_df = add_truncated_date_columns(songs_df)


# join_cols = []
# return_cols = []
# join_and_return(activities_df,songs_df, join_cols, return_cols)
new_df['played_at_trunc'] = new_df['closest_song_time_trunc']
final_df = new_df.merge(songs_df, on='played_at_trunc')

final_df=final_df.sort_values(by=['activity_start_time', 'played_at_y'], ascending=[False, True])
                 
# Rename Columns:
final_df = final_df.rename(columns={
    'played_at_y': 'song_start_ts',
    'played_at_x': 'activity_start_ts',
})

# final_df = final_df.reindex(final_df['song_start_ts'])

# Convert milliseconds to timedelta
# df['milliseconds'] = pd.to_timedelta(df['milliseconds'], unit='ms')

# # Create 'end_time' column by adding 'start_time' and 'milliseconds'
# df['end_time'] = df['start_time'] + df['milliseconds']

final_df['duration_ms'] = final_df['duration_ms']/1000
final_df['song_end_ts'] = final_df['song_start_ts'] + pd.to_timedelta(final_df['duration_ms'], unit='ms')
# Add Song_End Date

final_df['song_length'] = final_df['song_end_ts'] - final_df['song_start_ts']  

# minutes 
final_df['song_length_min']  = final_df['song_length'].dt.total_seconds()/60
final_df['song_length_min'] = final_df['song_length_min'].round(5)      

# seconds
final_df['song_length_sec']  = final_df['song_length'].dt.total_seconds()

# cumulative time on an activity
final_df['song_length_sec_cum']= final_df['song_length_sec'].cumsum()



# final_df_expanded = expand_dataframe(final_df)


# Artificial Activity end timestamp:
grouped_df = final_df.groupby(['activity_name','activity_start_time']).agg({'song_end_ts': 'max'})

# Rename the column
grouped_df = grouped_df.rename(columns={'song_end_ts': 'proxy_activity_end_ts'})
final_df = pd.merge(final_df, grouped_df, on=['activity_name','activity_start_time'])
# final_df_expanded.to_csv('runs_songs_big.csv', index=False)
final_df.to_csv('runs_songs.csv', index=False)



