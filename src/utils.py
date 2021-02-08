import os
import re
import shutil
import numpy as np
import pandas as pd

### Reset Repo ###
def reset():

    if os.path.exists('features.csv'):
        os.remove('features.csv')

### General Cleaning ###
def std_df(df, time):
    """
    Takes unix time and standardizes to [time unit] starting from 0.
    time is the time_column
    """
    df[time] = df[time] - df[time].min()
    return df

def filter_ip(df):
    """
    filters out local ip addresses
    """
    multicast = r'2[2-3][4-9].'
    multicast_IPv6 = r'FE02'
    linklocal = r'FE80'

    clean_df = df[
        ~df['IP1'].str.contains(multicast)][
        ~df['IP1'].str.contains(multicast_IPv6)][
        ~df['IP1'].str.contains(linklocal)][
        ~df['IP2'].str.contains(multicast)][
        ~df['IP2'].str.contains(multicast_IPv6)][
        ~df['IP2'].str.contains(linklocal)]

    return clean_df

### Extended Column Cleaning ###
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
          'Time': clean_ext_entry(row['packet_times'], dtype),
          'pkt_size': clean_ext_entry(row['packet_sizes'], dtype),
          'pkt_src': clean_ext_entry(row['packet_dirs'], str)
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
    df_lst = []

    df.apply(lambda x: df_lst.append(create_ext_df(x, np.int64)), axis=1)

    ms_df = pd.concat(df_lst)

    if sorted:
        ms_df = ms_df.sort_values(by=['Time'])

    ms_df['Time'] = pd.to_datetime(ms_df['Time'], unit='ms')

    # aggregate occurances that happen at the same second
    grouped_ms_src = ms_df.groupby(['Time', 'pkt_src']
                            ).agg({'pkt_size':'sum'}).reset_index()

    return grouped_ms_src

### Preprocess Helper ###
def label_data(df, video, labels):
    """
    video is a boolean; True if video and false else
    """

    if not labels:
        return df

    else:
        if video:
            df['video'] = np.ones(len(df))
        else:
            df['video'] = np.zeros(len(df))

    return df
