import dill
import pandas as pd
import numpy as np
import json
import sys

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, 'src')
from eda import *
from clean import *
from features import *

def main(targets):

    model_params = json.load(open('config/model-params.json'))

    test_params = json.load(open('config/test-params.json'))
    data_params = json.load(open('config/data-params.json'))

    clf = dill.load(open(model_params['model'], 'rb'))

    if 'clean' in targets:
        reset()

    if 'test' in targets:
        print('Creating EDA visuals. \n')
        eda_visuals(**test_params[0])
        print('Visuals completed. Located in ../test/visuals \n')

        print('Feature Creation In Progress. \n')
        test_feats = chunk_data(**test_params[1])
        print('Features Created!')
        print(test_feats)
        print('\n')

        print('Classifying data.')
        preds = clf.predict(test_feats)
        print(preds)

        print('\n')
        print('Testing complete. Run clean target to reset test.')

    if 'eda' in targets:
        eda_visuals(**data_params[0])
        print('EDA visuals located in ' + data_params[0]['outdir'] + '.')

    if 'predict' in targets:

        features = chunk_data(**data_params[1])
        features.to_csv('features.csv')

        print('Features located in "features.csv". \n')
        print('Video == 1; No Video == 0')
        preds = clf.predict(features)
        print(preds)

        print('Run clean target to reset folder.')

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
