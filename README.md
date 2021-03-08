# ResRecovery

Website: https://stephdoan.github.io/ResRecovery/

## Abstract

Virtual private networks, or VPNs, have seen a growth in popularity as more of the general population has come to realize the importance of maintaining data privacy and security while browsing the Internet. In previous works, our domain developed robust classifiers that could identify when a user was streaming video. As an extension, our group has developed a Random Forest model that determines the resolution at the time of video streaming.

## Config Files

#### train-params.json

Allows users to adjust some parameters of the training data creation process. The main point of focus is the `{interval}` argument. This allows users to adjust how big of a chunk size they would like their model to be trained on. The default is 300 seconds as it allows replication of our project.

| Parameter     | Description                                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------------------------- |
| folder_path   | path to where all of the raw data is stored; please refer to the folder structure below to achieve best results |
| interval      | chunk size                                                                                                      |
| threshold     | minimum megabit value; used in peak feature creation                                                            |
| prominence_fs | sampling rate to find the max peak prominence                                                                   |
| binned_fs     | deprecated parameter                                                                                            |

#### model-params.json

Allows users to adjust hyperparameters of the random forest classifier. The default values are the values we utilized in our original project.

| Parameter         | Description                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| training_data     | path to where training data is stored; data must be stored as a CSV file |
| n_estimators      | number of trees in the forest model                                      |
| max_depth         | max depth of the tree                                                    |
| min_samples_split | minimum number of samples required to split an internal node             |

#### user-data.json

| Parameter     | Description                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| path          | path to where all of the raw user data is stored; must be an output of [network-stats](https://github.com/viasat/network-stats) |
| interval      | chunk size                                                                                                                      |
| threshold     | minimum megabit value; used in peak feature creation                                                                            |
| prominence_fs | sampling rate to find the max peak prominence                                                                                   |
| binned_fs     | deprecated parameter                                                                                                            |

#### generate-data.json

| Parameter          | Description                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| network_stats_path | location of network-stats.py                                                                                    |
| interface          | user interface to collect from; refer to [network-stats](https://github.com/viasat/network-stats) documentation |
| playlist           | link to YouTube playlist                                                                                        |
| outdir             | to be implemented                                                                                               |
| resolutions        | list of resolutions to be collected                                                                             |

## Running the Project

- <code>python run.py test</code> will test the various targets to ensure that all methods are running properly.

- <code>python run.py clean</code> will delete files created from running various targets. The folder and files are deleted from the local machine.

- <code>python run.py features</code> will create features from data specified in <code>train-params.json</code>.

- <code>python run.py predict</code> will either create training data to create a model or utilize a Pickle'd model that we have included. Output is an array of resolution label for each chunk in the data.
