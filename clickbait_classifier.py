import json

import numpy
import sys

from flask import Response
from flask import request
from sklearn import preprocessing, svm
from sklearn.pipeline import Pipeline

import utility
from flask import Flask
app = Flask(__name__)

###############  Classifier  ############################
print "creating classifier..."
no_samples = 10000
positive = numpy.loadtxt("vectors/positive.csv", delimiter=',')
negative = numpy.loadtxt("vectors/negative.csv", delimiter=',')
X = numpy.concatenate((positive, negative), axis=0)
p = numpy.ones((no_samples, 1))
n = numpy.full((no_samples, 1), -1, dtype=numpy.int64)
Y = numpy.concatenate((p, n), axis=0)
y = Y.ravel()
# scale
scaler = preprocessing.StandardScaler().fit(X)
# classifying
svm_module = svm.SVC()
classifier = Pipeline(steps=[('svm', svm_module)])  # [('scale', scaler), ('svm', svm_module)])
classifier.fit(X, y)
print "Classifier created"


##############################################################

##################### Clickbait Classifier Service ###########################
def is_click_bait(document):
    try:
        title_vector = numpy.array(utility.create_vector(document)).reshape(1, -1)
        # t = scaler.transform(title_vector)
        prediction = classifier.predict(title_vector)
        if prediction[0] == 1:
            return "Clickbait"
        else:
            return "Normal"
    except Exception, e:
        print "except:", e



##### Flask app

@app.route('/q', methods=['POST'])
def login():
    if request.method == 'POST':
        result = {}
        j = request.get_json()
        try:
            content = j["input"]
        except KeyError:
            return Response("Sentence missing.\nPOST data as JSON dictionary with a key \'input\' .",
                            status=400)
        if isinstance(content, (list, tuple)):
            # {response: [{clickbait:True, sent:blabla}, ...]}
            output = [{"clickbait":is_click_bait(doc), "sent": doc} for doc in content]
        else:
            output = {"clickbait":is_click_bait(content), "sent": content}
        result = {"response": output}
        return Response(json.dumps(result), status=200, mimetype='application/json')


if __name__ == '__main__':
    mode = ""
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode == "server":
        app.run(host="0.0.0.0", port=4586)
    elif mode == "shell":
        input_text = "W"
        while input_text != "Q":
            input_text = raw_input("Enter a news headline or 'Q/q' to exit: ")
            if input_text == "Q" or input_text == 'q':
                break
            print is_click_bait(input_text)
        print "Exited Succesfully"
