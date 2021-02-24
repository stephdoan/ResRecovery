import os
import numpy as np
import pandas as pd

# Reset Repo 
def reset():

    if os.path.exists('features.csv'):
        os.remove('features.csv')

# Chunk Data
def chunk_data(df, interval=120):
    """
    takes in a filepath to the data you want to chunk and feature engineer
    chunks our data into a specified time interval
    each chunk is then turned into an observation to be fed into our classifier
    """
    df_list = []
    
    df['Time'] = df['Time'] - df['Time'].min()
    
    total_chunks = np.floor(df['Time'].max() / interval).astype(int)

    for chunk in np.arange(total_chunks):
      
        start = chunk * interval
        end = (chunk+1) * interval

        temp_df = (df[(df['Time'] >= start) & (df['Time'] < end)])
        
        df_list.append(temp_df)
        
    return df_list

# Extended Column Cleaning 
def clean_ext_entry(entry, dtype):
    """
    takes an entry, cleans the lists, and stores values in a numpy array.
    helper method for expand_ext

    parameters:
        entry: row entry from [packet_times, packet_sizes, packet_dirs]
        dtype: choose from [float, np.int64, np.float64]

    return:
        array of specified type
    """

    clean_str = entry[:-1].strip()
    split_str = clean_str.split(';')
    to_type = np.array(split_str).astype(dtype)
    return to_type

def create_ext_df(row, dtype, dummy_y=False, order=False):
    """
    takes in a row (series) from network-stats data and returns a dataframe
    of extended column entries

    parameters:
        row: row to expand into dataframe
        dtype: choose from [float, np.int64, np.float64]

    return:
        dataframe of collected packet details in a network-stats second
    """

    temp_df = pd.DataFrame(
        {
          'Time': row['packet_times'].apply(lambda x: x[:-1].split(';')).astype(dtype),
          'pkt_size': row['packet_dirs'].apply(lambda x: x[:-1].split(';')).astype(dtype),
          'pkt_src': row['packet_sizes'].apply(lambda x: x[:-1].split(';')).astype(dtype)
        }
    )

    if dummy_y:
        temp_df['dummy_y'] = np.zeros(len(temp_df))
    if order:
        temp_df['order'] = np.arange(len(temp_df))

    return temp_df

def convert_ms_df(df, sorted=True):
    """
    takes in a network-stats df and explodes the extended columns.
    time is converted from seconds to milliseconds.
    drop the ip address columns and the aggregate columns.
    """
    pkt_time = np.hstack((df['packet_times'].apply(lambda x: x[:-1].split(';')))).astype(np.int64)
    pkt_size = np.hstack((df['packet_sizes'].apply(lambda x: x[:-1].split(';')))).astype(int)
    pkt_dir = np.hstack((df['packet_dirs'].apply(lambda x: x[:-1].split(';')))).astype(int)

    ext_df = pd.DataFrame({
        'Time': pkt_time,
        'pkt_dir': pkt_dir,
        'pkt_size': pkt_size
    })

    sorted_df = ext_df.sort_values('Time')
    sorted_df['Time'] = pd.to_datetime(sorted_df['Time'], unit='ms')

    return sorted_df

# Peak Related 
def get_peak_loc(df, col, strict=1):
    """
    takes in a dataframe, column, and strictness level. threshold is determined
    by positive standard deviations from the average. strict is default at 1.

    returns an array of peak locations (index).
    """
    threshold = df[col].mean() + (strict * df[col].std())
    return np.array(df[col] > threshold)

# Add Resolution Column
def add_resolution(fp, res):
  temp_df = pd.read_csv(fp)
  temp_df['resolution'] = res
  return temp_df

# Read in all Data
