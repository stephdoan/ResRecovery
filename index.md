---
layout: default
---

# Overview

Virtual private networks, or VPNs, have seen a growth in popularity as more of the general population has come to realize the importance of maintaining data privacy and security while browsing the Internet. VPNs route their users’ network traffic data through their own private servers, allowing them to provide these users with extra anonymity and protection by disguising the details of their network activity. However, even with the loss of detail such as packet destination, user activity in a VPN tunnel is still identifiable.

Over the last ten weeks, we have built a classifier that is able to identify the resolution/quality of video while in a VPN tunnel. Our model is an extension of a previous binary classifer that was able to determine if a user was streaming video or not while in a VPN tunnel.

# The Data

Network traffic data was collected via the Viasat provided script, [network-stats](https://github.com/viasat/network-stats). The script collects details such as bytes being sent to the server/to the local machine on a second and millisecond level of detail.

Our dataset is comprised of over 25 hours of network traffic of video playback from YouTube. YouTube was our primary source of video data as it allows full autonomy over video quality. The data collection process was also automated via a Selenium script developed by a group member. Our dataset includes video resolutions:

```python
video_resolutions: ["144p", "240p", "360p", "480p", "720p", "1080p"]
```

In the final iteration of our model, we grouped the resolutions to be:

```python
low_resolution: ["144p", "240p"]
medium_resolution: ["360p", "480p"]
high_resolution: ["720p", "1080p"]
```

Attempting to classify the exact numeric resolution proved to be difficult as factor such as user's network conditions or maximum bandwidth affect how data is transmitted. A user with a slightly lower bandwidth than a peer's may be able to stream 1080p with no interruptions but they may receive slightly small byte payloads slightly more often. However, we can see visually see when more resources are required at certain resolution thresholds.

When constructing our model, we chose to use 5 minute chunks as it was enough data to capture trends and behaviors over time while being robust to things such as the initial loading of video (this event typically results in a sudden influx on data, causing even low resolution to be mistaken as high resolution).

### Download Byte Stream

For our purposes, we primarily focused on the downloaded bytes stream. We saw that as resolution increases so does the frequency and magnitude of data. However, the magnitude of data being downloaded increases first and then the frequency. We use this knowledge to create some thresholding features to help set preliminary boundaries between resolutions.

Below is an example of what the downloaded byte stream looks like for a single video at six different resolutions. The data was collected by one user to ensure that network conditions would introduce any random noise.

![Download Byte Stream](img/download_byte_stream.png)

### Peaks

A focus point of our model is looking at the large downloads being sent in a single second. Data peaks/spikes are defined as a large transaction of data in a single second. Large is relative to the resolution but we found that using a hard threshold of 5 megabits produced subsets of data where many features could be extracted. Much like before, we take some basic aggregate statistics to describe the magnitude and spread of the peaks. But the most useful feature in our model from this peaks data is the time between peaks. If we look back to the downloaded byte stream, we can see that there are much less peaks in the lower resolutions. Below are boxplots to help visualize the spread in average peak value as well as the seconds per peak ratio. Notice that these two features seem to have a negatively correlated relationship.

![Peaks](img/peaks_visual.png)

### Spectral Analysis

Much of our spectral features came from trying to characterize the resultant periodograms after applying Welch's method. [Network-stats](https://github.com/viasat/network-stats) allows analysis on a millisecond level, and in turn, allowing us to capture [higher frequency signals](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem). But, even at high resolutions, the most commonly observed frequency of the strongest signal lies between the .2Hz - .3Hz. As a result, we rebin our data to be samples spaced at 2 seconds.

In the graphic below, we can see that higher resolutions have much stronger signals being picked up by Welch's method than the lower resolutions.

![Periodograms](img/periodograms.png)

# Features

Below is a list and summary of all the features we used in our model. Every feature was made in

| Features         | Description                                                                                                                                                                                                                                                                                                                                                                    |
| :--------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| download_avg     | The average bytes per second in the download direction.                                                                                                                                                                                                                                                                                                                        |
| download_std     | The standard deviation of the bytes in the download direction.                                                                                                                                                                                                                                                                                                                 |
| peak_avg         | The average byte amount of data peaks in the download direction. Peaks are defined as any single second transfer of data that is greater than 5 megabits.                                                                                                                                                                                                                      |
| peak_std         | The standard deviation of byte amount of data peaks in the download direction.                                                                                                                                                                                                                                                                                                 |
| peak_amount      | The total number of data peaks in the download direction.                                                                                                                                                                                                                                                                                                                      |
| seconds_per_peak | The ratio of seconds to peaks.                                                                                                                                                                                                                                                                                                                                                 |
| max_prominence   | Max prominence of the strongest signal in a periodogram (represented as the tallest peak in the graph). The frequency and power values are generated by applying Welch's methods on a 2 second resampled version of the data. Peaks in the periodogram are found by using SciPy's find_peaks method and the prominence values are calculated for data points considered peaks. |
| prominence_std   | In the periodograms, high resolution data generates well defined peaks while lower resolution does not. In our max_prominence feature, we calculate the prominence values for all the peaks found in the data. We simply run take the standard deviation of this array to create this prominence_std feature.                                                                  |
| rolling_cv       | Coefficient of variation taken over a rolling window version of the data                                                                                                                                                                                                                                                                                                       |

## Feature Importance

# Model

We found that a Random Forest classifier performed best. The model is able to give a low, medium, and high label when fed output data from [network-stats](https://github.com/viasat/network-stats). With very little hyperparameter tuning, our model is able to achieve an accuracy 88%. More importantly, there are very few misclassifications that span beyond neighboring labels (e.g. none of the low resolution was misclassified as high).
