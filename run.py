import dill
import pandas as pd
import numpy as np
import json
import sys

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, 'src')
from utils import *
from features import *

def main(targets):

    model_params = json.load(open('config/model-params.json'))
    test_params = json.load(open('config/test-params.json'))
    data_params = json.load(open('config/data-params.json'))

    clf = dill.load(open(model_params['model'], 'rb'))

    if 'clean' in targets:
      reset()

    if 'test' in targets:

      print('Feature Creation In Progress. \n')

      test_feats = create_features(**test_params)
      print('Features Created!')
      print(test_feats)
      print('\n')

      print('Classifying data.')
      preds = clf.predict(test_feats)
      print(preds)

      print('\n')
      print('Testing complete. All targets running properly. Run clean target to reset test.')

    if 'features' in targets:
      features = create_features(**data_params)
      features.to_csv('features.csv')

    if 'predict' in targets:

      features = create_features(**data_params)
      features.to_csv('features.csv')

      print('Features located in "features.csv". \n')
      print('Video == 1; No Video == 0')
      preds = clf.predict(features)
      print(preds)

      print('Run clean target to reset folder.')

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
