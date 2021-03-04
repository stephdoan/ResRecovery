import numpy as np
import pandas as pd
import scipy as sp
from scipy.signal import find_peaks
from utils import *

### Aggregate Features ###
def agg_feat(df, col):
    """
    takes in a dataframe and a column. column values should be numeric.
    returns the mean, and standard deviation of the column.
    """
    return [np.mean(df[col]), np.std(df[col])]


### Peak Related Aggregate Features ###
def peak_time_diff(df, col):
    """
    mess around with the different inputs for function.
    variance seems to inflate the difference betweent the two the most with litte
    to no data manipulation. however, currently trying things like
    squaring the data before taking the aggregate function to exaggerate
    differences (moderate success??)
    """
    peaks = df[get_peak_loc(df, col)]
    peaks['Time'] = peaks['Time'] - peaks['Time'].min()
    time_diff = np.diff(peaks['Time'] ** 2)
    return [np.mean(time_diff), np.var(time_diff), np.std(time_diff)]

### Spectral Features ###
"""
TODO
- take some aggregate value of binned frequency (e.g. what should we expect
to see in a range of frequencies for x resolution?)
- try to determine frequency relativeness and compare from there (this is
mostly related to relativeness within the data itself and not across
resolutions)
- do more with rolling windows (small windows catch the details, big windows catch
the overall behavior)
"""
def spectral_features(df, col):

    """
    welch implemention of spectral features.
    resample the data before inputting (might change prereq depending on
    resource allocation).
    """

    f, Pxx_den = sp.signal.welch(df[col], fs = 2)
    Pxx_den = np.sqrt(Pxx_den)

    peaks = sp.signal.find_peaks(Pxx_den)[0]
    prominences = sp.signal.peak_prominences(Pxx_den, peaks)[0]

    idx_max = prominences.argmax()
    loc_max = peaks[idx_max]

    return [f[loc_max], Pxx_den[loc_max], prominences[idx_max]]

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

def binned_freq(placeholder):
    """
    dummy implementation of binned frequencies
    """
    return

def rolling_window(placeholder):
    """
    dummy implementation of rolling window features
    """
    return

### Create Features ###
def chunk_data(df, interval=60):
    """
    takes in a dataframe and an interval defined in seconds.
    returns a list of dataframes of equal time.
    """
    df_list = []

    # normalizes unix time to be seconds from start
    df['Time'] = df['Time'] - df['Time'].min()

    total_chunks = np.floor(df['Time'].max() / interval).astype(int)

    for chunk in np.arange(total_chunks):

        start = chunk * interval
        end = (chunk+1) * interval

        temp_df = df[(df['Time'] >= start) & (df['Time'] < end)]

        df_list.append(temp_df)

    return df_list

def create_features(filepath, interval=60):

    features = [
        'dwl_peak_freq',
        'dwl_max_psd',
        'dwl_peak_prom',
        'dwl_bytes_avg',
        'dwl_bytes_std',
        'dwl_peak_avg',
        'dwl_peak_var',
        'dwl_peak_std',
        'upl_peak_freq',
        'upl_max_psd',
        'upl_peak_prom',
        'upl_bytes_avg',
        'upl_bytes_std',
        'upl_peak_avg',
        'upl_peak_var',
        'upl_peak_std',
        'IMAN_dwn_time_peak',#'IMAN_up_time_peak',
        'IMAN_dwn_num_peak'#,'IMAN_up_num_peak'
    ]

    vals = []

    df = pd.read_csv(filepath)

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
        iman_dwn_time_peak = np.mean(peak_times(chunk,'2->1Bytes',1000000))
        #iman_up_time_peak = np.mean(peak_times(chunk,'1->2Bytes',50000))

        ## iman's num peak
        iman_dwn_num_peak = num_peaks(chunk,'2->1Bytes',1000000)
        #iman_up_num_peak = num_peaks(chunk,'1->2Bytes',50000)

        feat_val = np.hstack((
            dwl_spectral,
            dwl_agg,
            dwl_peak,
            upl_spectral,
            upl_agg,
            upl_peak,
            iman_dwn_time_peak,
            #iman_up_time_peak,
            iman_dwn_num_peak,
            #iman_up_num_peak
        ))

        vals.append(feat_val)

    return pd.DataFrame(columns=features, data=vals).fillna(0)
