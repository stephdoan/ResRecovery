import os
import re
import numpy as np
import pandas as pd


### Reset Repo ###
def reset():
    if os.path.exists('features.csv'):
        os.remove('features.csv')


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


def convert_ms_df(df, agg=True, sorted=True):
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
    if agg:
        grouped_ms_src = ms_df.groupby(['Time', 'pkt_src']
                                       ).agg({'pkt_size': 'sum'}).reset_index()

        return grouped_ms_src
    else:
        return ms_df


### Peak Related ###
def get_peak_loc(df, col, strict=1):
    """
    takes in a dataframe, column, and strictness level. threshold is determined
    by positive standard deviations from the average. strict is default at 1.
    returns an array of peak locations (index).
    """
    threshold = df[col].mean() + (strict * df[col].std())
    return np.array(df[col] > threshold)
