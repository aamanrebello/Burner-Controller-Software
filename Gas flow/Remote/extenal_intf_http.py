from flask import Flask, request, jsonify

from multiple_regression import MR_predictor
from linear_regression import LR_predictor

import csv

# This module serves as an external interface for the machine learning modules to communicate with the edge device.
# The main program on the edge device can train the ML modules remotely and provide data to receive the precdictions
# back.

# This interface uses high level HTTP implemented with the help of flask.

app = Flask(__name__)
api = Api(app)

# Create object of linear regression predictor class.
LR_P = LR_predictor()

# Create object of multiple regression predictor class.
MR_P = MR_predictor()

# Open csv file to receive data
DATAFILE = open('ML/data/labelled_data.csv', 'w', newline='')
# Csv file writing object
FILEWRITER = csv.writer(DATAFILE)
# Write row headers.
FILEWRITER.writerow(["G", "P", "A", "output"])

#-----------------------------------------------------------------------------------------
# This function can be remotely called to train ML models.
@app.route("/train" , methods = ['GET'])
def train_models():
    try:
        # Train LR.
        LR_m, LR_c = LR_P.find_line()
        # Train MR.
        mr_p.train_and_test()
        # Return line coefficients.
        response = {"LR_m": LR_m, "LR_c": LR_c}
        return jsonify(response), 200

    # Account for HTTP Exception
    except HTTPError as http_err:
        return "HTTP error", 404
    except:
        return "Error", 404


#------------------------------------------------------------------------------------------
# This function can be remotely called to make predictions using multiple regression.
@app.route("/MR_predict" , methods = ['POST'])
def predict_MR():
    try:
        # Receive json data.
        P = int(request.json["supply_pressure"])
        A = int(request.json["air_aperture"])
        output = int(request.json["output"])

        result = MR_P.predict(P, A, output)
        if result is not None:
            return str(result), 200
        else
            return "", 404
    # Account for HTTP Exception
    except HTTPError as http_err:
        return "HTTP error", 404
    except:
        return "Error", 404


#--------------------------------------------------------------------------------------------
# This function is remotely called to provide new data to the ML system. It receives the
# readings in JSON format and adds it to a numpy array.
@app.route("/newdata" , methods = ['POST'])
def add_data():
    try:
        # Receive json data.
        P = int(request.json["supply_pressure"])
        A = int(request.json["air_aperture"])
        G = int(request.json["gas_aperture"])
        output = int(request.json["output"])

        # all the parameters 0 indicates that the data stream has finished and so we close the file.
        if P == 0 and A == 0 and G == 0 and output == 0:
            DATAFILE.close()
        # Else write the next row.
        else:
            FILEWRITER.writerow([G, P, A, output])

    # Account for HTTP Exception
    except HTTPError as http_err:
        return "HTTP error", 404
    except:
        return "Error", 404

#-----------------------------------------------------------------------------------------------------------
#END#
