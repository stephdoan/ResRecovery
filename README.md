## ResRecovery

Website: https://stephdoan.github.io/ResRecovery/

Working repository of model that is able to identify video resolution from extended network-stats output. Current implementation identifies [`240p, 480p, 1080p`]. Other resolutions are currently mis-classified as one of the three listed.

## Setting User Data

Change [`fp`] in <code>data-params.json</code> to filepath of data you wish to identify video resolution from.

Changing the chunk size of user data has no impact on the actual classifier. The classifier is preset to 60 seconds but users are able to create their own instance of the model by collecting data from various resolutions.

## Running the Project

<ul>
  <li>
    <code>python run.py clean</code> will delete files created from running various targets. The folder and files are deleted from the local machine.
  </li>

  <li>
    <code>python run.py test</code> will test the various targets to ensure that all methods are running properly.
  </li>

  <li>
    <code>python run.py features</code> will create features from data specified in <code>data-params.json</code>.

  <li>
    <code>python run.py predict</code> will use our trained model to predict results from new data. It is not necessary to run <code>features</code> as feature creation is accounted for in this target.
  </li>
</ul>
