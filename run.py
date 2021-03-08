import os
import sys
import json
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")

import src
from src.features import create_features, create_training_data
from src.model import create_model

def main(targets):

    test_params = json.load(open('config/test-params.json'))
    user_params = json.load(open('config/user-data.json'))
    train_params = json.load(open('config/train-params.json'))
    model_params = json.load(open('config/model-params.json'))

    if 'test' in targets:
      print('creating training_data from test data')
      test_training = create_training_data(**test_params[0])
      test_training.to_csv('test_training.csv', index=False)
      print('training data created from test sets. now constructing model.')
      clf = create_model(**test_params[1])
      print('model trained. testing prediction function on test set.')

      test_data = create_features(**test_params[2])
      test_prediction = clf.predict(test_data)
      print('model should predict "high".')
      print(test_prediction)

      src.utils.reset()
      print('repo now cleaned')

    if 'clean' in targets:
      src.utils.reset()
      print('clean repo')

    if 'train' in targets:
      training_data = create_training_data(**train_params)
      training_data.to_csv('training.csv', index=False)
      print('Training data saved in training.csv')

    if 'predict' in targets:

      if os.path.exists('training.csv'):
        print('Training data exists.')

      else:
        print('Please wait as training data is created.', flush=True)
        training_data = create_training_data(**train_params)
        training_data.to_csv('training.csv', index=False)
      
      clf = create_model(**model_params)

      user_data = create_features(**user_params)

      user_prediction = clf.predict(user_data)
      print(user_prediction)

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
