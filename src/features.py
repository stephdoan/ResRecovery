import numpy as np
import pandas as pd
import scipy as sp

from utils import *

### Rolling Window Features ###
"""
Definitely looking to add more rolling features in the future. Hopefully, ones
that are less convoluted than the current normalized standard deviation
"""
def rolling_normalized_std(df, sample_size):
    """
    takes in the resampled convert_ms_df output
    finds the normalized standard deviation of the peaks created
    from rolling windows.
    """

    df_roll = df.rolling(sample_size, on='Time').mean()
    df_roll_mean = df_roll['pkt_size'].mean()

    roll_peaks = sp.signal.find_peaks(
    df_roll['pkt_size'], height = df_roll_mean)

    peak_std = df_roll.iloc[roll_peaks[0]]['pkt_size'].std()
    peak_mean = df_roll.iloc[roll_peaks[0]]['pkt_size'].mean()

    normalized_std = peak_std / peak_mean

    return normalized_std

### Packet Ratio Feature ###
def packet_ratio(df, sample_size):
    """
    takes in the output of convert_ms_df.
    """
    src_grouped = df.groupby(
    'pkt_src').resample(
    sample_size, on='Time')[
    'pkt_size'].count().reset_index()

    upl_pkts = src_grouped[src_grouped['pkt_src'] == '1']['pkt_size'].values
    dwl_pkts = src_grouped[src_grouped['pkt_src'] == '2']['pkt_size'].values

    ratio = np.sum(upl_pkts) / np.sum(dwl_pkts)

    return ratio

### Spectral Features ###
def spectral_features(df, col):

    """
    welch implemention of spectral features
    """

    f, Pxx_den = sp.signal.welch(df[col], fs=2)
    Pxx_den = np.sqrt(Pxx_den)

    peaks = sp.signal.find_peaks(Pxx_den)[0]
    prominences = sp.signal.peak_prominences(Pxx_den, peaks)[0]

    idx_max = prominences.argmax()
    loc_max = peaks[idx_max]

    return [f[loc_max], Pxx_den[loc_max], prominences[idx_max]]

### Feature Creation ###
"""
Creates features from network-stats output
"""
def chunk_data(fp, interval=100, select_col=[
    'Time',
    '1->2Bytes',
    '2->1Bytes',
    '1->2Pkts',
    '2->1Pkts',
    'packet_times',
    'packet_sizes',
    'packet_dirs'
    ]):

    """
    takes in a filepath to the data you want to chunk and feature engineer
    chunks our data into a specified time interval
    each chunk is then turned into an observation to be fed into our classifier
    """

    chunk_feature = []
    chunk_col = [
        'dwl_freq',
        'dwl_max_psd',
        'dwl_peak_prominence',
        'upl_freq',
        'upl_max_psd',
        'upl_peak_prominence',
        'freq_diff',
        'rolling_normalized_std_bytes',
        'pkt_ratio'
    ]

    df = filter_ip(std_df(pd.read_csv(fp), 'Time'))[select_col]

    total_chunks = np.floor(df['Time'].max() / interval).astype(int)

    for chunk in np.arange(total_chunks):

        start = chunk * interval
        end = (chunk+1) * interval

        temp_df = (df[(df['Time'] >= start) & (df['Time'] < end)])

        preproc = convert_ms_df(temp_df)

        upl_bytes = preproc[preproc['pkt_src'] == '1'].resample('500ms', on='Time').sum()
        dwl_bytes = preproc[preproc['pkt_src'] == '2'].resample('500ms', on='Time').sum()

        dwl_spectral = spectral_features(dwl_bytes, 'pkt_size')
        upl_spectral = spectral_features(upl_bytes, 'pkt_size')

        freq_diff = dwl_spectral[0] - upl_spectral[0]

        rolling_feature = rolling_normalized_std(preproc, '20s')

        pkt_ratio = packet_ratio(preproc, '20s')

        chunk_feature.append(np.hstack((
          dwl_spectral,
          upl_spectral,
          freq_diff,
          rolling_feature,
          pkt_ratio
        )))

    return pd.DataFrame(data=chunk_feature, columns=chunk_col)


### Create training data ###
def create_training_data(fp_lst, data_fp, fldr=''):
    """
    creates training data by reading in files and chunking them.
    concatenates multiple data frames into one big one.
    stream takes in [True, False] - true means data being fed is streaming and vice versa
    """
    video_df = pd.DataFrame()
    novideo_df = pd.DataFrame()

    providers = r"amazonprime|disneyplus|espnplus|\
              hbomax|hulu|netflix|vimeo|youtube"

    for i in organize_data(data_fp)[1]:
        video_df = pd.concat([chunk_data(fldr + i), video_df])

    video_df['stream'] = np.repeat(1, len(video_df))

    for i in organize_data(data_fp)[0]:
        novideo_df = pd.concat([chunk_data(fldr + i), novideo_df])

    novideo_df['stream'] = np.repeat(0, len(novideo_df))

    return pd.concat([video_df, novideo_df]).reset_index(drop=True)
