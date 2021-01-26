import os
import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns

import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from utils import *

def line_comp(df1, df2, col, title, rate=1):
    df1 = std_df(df1, 'Time')
    df2 = std_df(df2, 'Time')

    group_df1 = df1.groupby('Time')[[col]].sum()
    group_df2 = df2.groupby('Time')[[col]].sum()

    sns.set(rc={'figure.figsize':(20,5)})

    fig = plt.figure()

    fig.plot(group_df1[col] * rate, label = 'No Video')
    fig.plot(group_df2[col] * rate, label = 'Video')

    fig.legend(loc = 'upper left')
    fig.title(title, fontsize=24)
    fig.xlabel('Seconds (from the start)', fontsize=16)
    fig.ylabel('Bytes', fontsize=16)

    return fig


def plot_packet_flow(df, row_num, title, start, end):

    df_std = std_df(df, 'Time')
    df_peak = df_std[df_std['Time'] == row_num]
    df_peak_df = create_ext_df(df_peak.iloc[0], np.int64, dummy_y=True, order=True)

    sns.set(rc={'figure.figsize':(20,5)})

    fig = sns.scatterplot(
        data=df_peak_df[start:end],
        x='order', y='dummy_y', hue='pkt_src',
        style='pkt_src', palette=sns.color_palette("Set1", 2), s=120
    )

    fig.legend(loc =  'upper left')

    fig.set_title(title, fontsize = 20)

    return df_peak_df
