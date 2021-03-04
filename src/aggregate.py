import os
import sys
import re
import numpy as np
import pandas as pd
import scipy as sp
from scipy import signal
from scipy.signal import find_peaks
from features import *
from utils import *


# take the aggregate features of the whole chunk; download and upload
def agg_feat(df, col):
    return [np.mean(df[col]), np.std(df[col])]

## take the ratio of upload:download packets
def pkt_ratio(df):
    ms_df = convert_ms_df(df, True)
    local = np.sum(ms_df['pkt_src'] == '1')
    server = np.sum(ms_df['pkt_src'] == '2')
    return local / server

## take the ratio of upload:download bytes
def bytes_ratio(df):
    local = df['1->2Bytes'].sum()
    server = df['2->1Bytes'].sum()
    return local / server


## finds the peaks with mean + 2(1) std
## run the above aggregate functions on the peaks only??

def get_peak_loc(df, col, invert=False):
    'invert arg allows you to get values not considered peaks'
    df_avg = df[col].mean()
    df_std = df[col].std()

    threshold = df_avg + (1 * df_std)

    if invert:
        return np.array(df[col] < threshold)

    else:
        return np.array(df[col] > threshold)


## np.mean, np.var, np.std - think of more?
def peak_time_diff(df, col):
    '''
    mess around with the different inputs for function.
    variance seems to inflate the difference betweent the two the most with litte
    to no data manipulation. however, currently trying things like
    squaring the data before taking the aggregate function to exaggerate
    differences (moderate success??)
    '''
    peaks = df[get_peak_loc(df, col)]
    peaks['Time'] = peaks['Time'] - peaks['Time'].min()
    time_diff = np.diff(peaks['Time'] ** 2)
    return [np.mean(time_diff), np.std(time_diff)]


def peak_times(df,col,thresh):
    x = df[col]
    peaks, _ = find_peaks(x, height=thresh)
    if list(peaks) == []:
        return [-1]
    times = df.iloc[peaks]['Time'].values
    time_between_peaks = [times[i]-times[i-1]for i in range(1,len(times))]
    #print(time_between_peaks)
    #time_between_peaks[0]=0
    if time_between_peaks == []:
        return -1
    return time_between_peaks

def num_peaks(df,col,thresh):
    x = df[col]
    peaks, _ = find_peaks(x, height=thresh)
    return len(peaks)


def spectral_features(df, col):
    """
    welch implemention of spectral features
    resample the data before inputting (might change prereq depending on
    resource allocation)
    """
    f, Pxx_den = sp.signal.welch(df[col], fs=2)
    Pxx_den = np.sqrt(Pxx_den)

    peaks = sp.signal.find_peaks(Pxx_den)[0]
    prominences = sp.signal.peak_prominences(Pxx_den, peaks)[0]

    idx_max = prominences.argmax()
    loc_max = peaks[idx_max]

    return [f[loc_max], Pxx_den[loc_max], prominences[idx_max]]


## wip; need to decide chunk size eventually
## should we also make this chunking feature be our feature creation?

def chunk_data(df, interval=60):
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
        end = (chunk + 1) * interval

        temp_df = (df[(df['Time'] >= start) & (df['Time'] < end)])

        df_list.append(temp_df)

    return df_list


def create_features(dfs, interval=60):
    features = [
        'dwl_peak_freq',
        'dwl_peak_prom',
        'dwl_max_psd',
        'dwl_bytes_avg',
        'dwl_bytes_std',
        'dwl_peak_avg',
        'dwl_peak_std',
        'upl_peak_freq',
        'upl_peak_prom',
        'upl_max_psd',
        'upl_bytes_avg',
        'upl_bytes_std',
        'upl_peak_avg',
        'upl_peak_std',
        'dwl_time_peak',  # 'IMAN_up_time_peak',
        'dwl_num_peak'  # ,'IMAN_up_num_peak'
    ]

    vals = []
    for df in dfs:
        df_chunks = chunk_data(df, interval)

        for chunk in df_chunks:
            preproc = convert_ms_df(chunk, True)
            upl_bytes = preproc[preproc['pkt_src'] == '1'].resample('500ms', on='Time').sum()
            dwl_bytes = preproc[preproc['pkt_src'] == '2'].resample('500ms', on='Time').sum()

            ## spectral features
            dwl_spectral = spectral_features(dwl_bytes, 'pkt_size')
            upl_spectral = spectral_features(upl_bytes, 'pkt_size')

            ## aggregate features
            dwl_agg = agg_feat(chunk, '2->1Bytes')
            upl_agg = agg_feat(chunk, '1->2Bytes')

            ## peak features
            dwl_peak = peak_time_diff(chunk, '2->1Bytes')
            upl_peak = peak_time_diff(chunk, '1->2Bytes')

            ## iman's time between peak
            iman_dwn_time_peak = np.mean(peak_times(chunk, '2->1Bytes', 1000000))
            # iman_up_time_peak = np.mean(peak_times(chunk,'1->2Bytes',50000))

            ## iman's num peak
            iman_dwn_num_peak = num_peaks(chunk, '2->1Bytes', 1000000)
            # iman_up_num_peak = num_peaks(chunk,'1->2Bytes',50000)

            feat_val = np.hstack((
                dwl_spectral,
                dwl_agg,
                dwl_peak,
                upl_spectral,
                upl_agg,
                upl_peak,
                iman_dwn_time_peak,  # iman_up_time_peak,
                iman_dwn_num_peak,  # iman_up_num_peak
            ))

            vals.append(feat_val)

    return pd.DataFrame(columns=features, data=vals).fillna(0)
