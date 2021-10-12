from flask import Flask, request, jsonify
from flask_restful import Api
from ML.multiple_regression import MR_predictor
from ML.linear_regression import LR_predictor

import numpy as np

# This module serves as an external interface for the machine learning modules to communicate with the edge device.
# The main program on the edge device can train the ML modules remotely and provide data to receive the precdictions
# back.

# This interface uses high level HTTP implemented with the help of flask.

app = Flask(__name__)
api = Api(app)

# CLASS---------------------------------------------------------------------------------------------------------------
# First we define a class to perform the basic ML related and file writing functions
class external_interface:

    # Constructor initialises class variables and sets up csv files
    def __init__(self):
        # Create object of linear regression predictor class.
        self.__lr_p = LR_predictor()
        # Create object of multiple regression predictor class.
        self.__mr_p = MR_predictor()
        # Create numpy array to store new data (1 row, 4 columns).
        self.__datastore = np.empty(shape = (1,4))

#-------------------------------------------------------------------------------
    # This function is used to find out if it is possible to use ML (based on availability of data)
    def EI_check_ML(self):
        return self.__lr_p.use_lr()

#-------------------------------------------------------------------------------
    # Trains the ML models, returns coefficients of linear regression.
    def EI_train_models(self):
        # Train LR.
        LR_m, LR_c = self.__lr_p.find_line()
        # Train MR.
        self.__mr_p.train_and_test()
        # Return line coefficients.
        return {"LR_m": LR_m, "LR_c": LR_c}

#-------------------------------------------------------------------------------
    # Make predictions using multiple regression.
    def EI_predict_MR(self, P, A, output):
        return self.__mr_p.predict(P, A, output)

#-------------------------------------------------------------------------------
    # Save provided readings into local numpy array - for performance we only
    # write to the file after all the data has been sent.
    def EI_add_data(self, G, P, A, output):
        # store new data as numpy array.
        newdata = np.array([[G, P, A, output]])
        self.__datastore = np.concatenate((self.__datastore, newdata), axis = 0)

#-------------------------------------------------------------------------------
    # This function is used to close the csv file when writing is complete.
    def EI_end_of_data(self, filename='labelled_data'):
        fname = 'ML/data/' + filename + '.csv'
        # note that in the beginning we declared datastore as an empty matrix,
        # so now there will be an unwanted row of zeroes at the top of our
        # matrix. We get rid of it here.
        self.__datastore = np.delete(self.__datastore, (0), axis=0)
        # now save to csv file.
        np.savetxt(fname, self.__datastore, delimiter = ',', header = 'G,P,A,output')

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------




#API-----------------------------------------------------------------------------------------------------------------------
# Now we define the external-facing API functions that receives the requests and provides responses.

#-------------------------------------------------------------------------------

# define variable to hold object of external interface class
EX_INF = None

#-------------------------------------------------------------------------------
# Initialise above class.
@app.route("/initialise" , methods = ['GET'])
def API_initialise():
    try:
        global EX_INF
        EX_INF = external_interface()
        return "Initialisation Successful.", 200
    # Account for Exception
    except Exception as e:
        return str(e), 404

#-------------------------------------------------------------------------------
# Check if ML can be used.
@app.route("/check_ML" , methods = ['GET'])
def API_check_ML():
    try:
        if EX_INF.EI_check_ML():
            return "ML can be used.", 200
        else:
            return "ML cannot be used - no data", 501
    # Account for Exception
    except Exception as e:
        return str(e), 404

#-------------------------------------------------------------------------------
# This function can be remotely called to train ML models.
@app.route("/train" , methods = ['GET'])
def API_train_ML():
    try:
        response = EX_INF.EI_train_models()
        # Check that LR was trained successfully.
        if response['LR_m'] == 0 and response['LR_m'] == 0:
            return "LR does not satisfy requirements", 500
        # if so, return response as JSON
        return jsonify(response), 200
    # Account for Exception
    except Exception as e:
        return str(e), 404

#-------------------------------------------------------------------------------
# This function can be remotely called to make predictions using multiple regression.
@app.route("/MR_predict" , methods = ['POST'])
def API_MR_prediction():
    try:
        # Receive json data.
        P = float(request.json["supply_pressure"])
        A = float(request.json["air_aperture"])
        output = float(request.json["output"])

        # generate and return result
        result = EX_INF.EI_predict_MR(P, A, output)
        if result == 0.0:
            return "MR Prediction does not satisfy requirements.", 500
        else:
            return str(result), 200
    # Account for Exception
    except Exception as e:
        return str(e), 404

#-------------------------------------------------------------------------------
# This function is remotely called to provide new data to the ML system. It receives the
# readings in JSON format and passes it to the EI object.
@app.route("/newdata" , methods = ['POST'])
def API_add_data():
    try:
        # Receive json data.
        P = float(request.json["supply_pressure"])
        A = float(request.json["air_aperture"])
        G = float(request.json["gas_aperture"])
        output = float(request.json["output"])

        EX_INF.EI_add_data(G, P, A, output)
        return "Data add successful.", 200
    # Account for Exception
    except Exception as e:
        return str(e), 404

#-------------------------------------------------------------------------------
# This function is used to save accumulated data into csv file.
@app.route("/finishdata/<filename>" , methods = ['GET'])
def API_end_of_data(filename):
    try:
        EX_INF.EI_end_of_data(filename)
        return "data saved successfully", 200
    # Account for Exception
    except Exception as e:
        return str(e), 404

#---------------------------------------------------------------------------------------------------
# Run the web app to act as the server i.e. external interface
if __name__ == '__main__':
    app.run(port ='8000', debug = True)

#--------------------------------------------------------------
#END#
