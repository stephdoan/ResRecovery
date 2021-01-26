def fft_func(df):

    """
    FFT implemention of spectral features (not used in model)
    """

    filtered = filter_ip(df)

    ms = convert_ms_df(filtered)
    flow = ms[ms['pkt_src'] == src]
    resampled = flow.resample('500ms', on='Time').sum().reset_index()

    fft = sp.fft.fft(resampled['pkt_size'])
    amp = np.abs(fft)
    psd = amp ** 2

    freq = sp.fft.fftfreq(len(fft), .5)

    idx = freq > 0

    peaks = sp.signal.find_peaks(Pxx_den)[0]
    prominences = sp.signal.peak_prominences(Pxx_den, peaks)[0]

    idx_max = prominences.argmax()
    loc_max = peaks[idx_max]

    return [f[loc_max], Pxx_den[loc_max], prominences[idx_max]]
