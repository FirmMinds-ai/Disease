import pickle

from flask import Flask, render_template, request, url_for

import numpy as np
from flask import jsonify
# initiate flask
app = Flask(__name__)


with open('std.pkl', 'rb') as file:
    scaler = pickle.load(file)


with open('lr.pkl', 'rb') as file:
    lr = pickle.load(file)


@app.route('/pred1/',methods = ['POST'])
def home() :

    if request.method == 'POST':
        data = request.get_json()
        print(data)
        l = data["data"]
        Inp = []
        for x in l :
            Inp.append(int(x))
        X = scaler.transform([Inp])

        out = lr.predict(X)[0]

        d = {"Prediction" : int(out)}

    return jsonify(d)


if __name__ == '__main__':
    app.run(debug = True)
