import os
import sys
import numpy as np
from scipy import stats
import pandas as pd
import pickle, dill
import io
from io import StringIO
import sklearn
from flask import Flask, render_template, request, jsonify, make_response
from utils import *
from features import *
from aggregate import *
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
#model = dill.load(open("./model/randomforest_chkpt2.obj", "rb"))
baseline_model = pickle.load(open("./model/baseline_model.pkl", "rb"))
extended_model = pickle.load(open("./model/extended_model.pkl", "rb"))
chunk_size = 120


@app.route('/')
def home():
    return render_template('index.html')


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")


@app.route('/baseline', methods=["POST"])
def predict_baseline():
    f = request.files['data_file']
    if not f:
        return "No file"

    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    stream.seek(0)
    result = transform(stream.read())
    df = pd.read_csv(StringIO(result))

    # Preprocessing & Feature Building
    X = create_features([df], chunk_size)
    X = X[['dwl_bytes_avg', 'dwl_peak_prom', 'upl_bytes_std', 'dwl_bytes_std', 'dwl_max_psd', 'dwl_num_peak']]
    prediction = stats.mode(extended_model.predict(X))[0][0]
    resolutions = {1: "240p", 2: "480p", 3: "1080p"}

    return render_template('index.html',
                           prediction_text_extended='The predicted resolution is: {}'.format(resolutions[prediction]))


@app.route('/extended', methods=["POST"])
def predict_extended():
    f = request.files['data_file']
    if not f:
        return "No file"

    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    stream.seek(0)
    result = transform(stream.read())
    df = pd.read_csv(StringIO(result))

    # Preprocessing & Feature Building
    X = create_features([df], chunk_size)
    X = X[['dwl_bytes_avg', 'dwl_peak_prom', 'upl_bytes_std', 'dwl_bytes_std', 'dwl_max_psd', 'dwl_num_peak']]
    prediction = stats.mode(extended_model.predict(X))[0][0]
    resolutions = {1: "Low", 2: "Medium", 3: "High"}

    return render_template('index.html',
                           prediction_text_extended='The predicted resolution is: {}'.format(resolutions[prediction]))


if __name__ == '__main__':
    app.run(port=8080, debug=True)
