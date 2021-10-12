from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler

import pandas as pd
import os

from math import sqrt

# MR_predictor: This class is used to predict the required gas aperture size using multiple regression with
# the relevant variables i.e. supply pressure (P), air aperture (A) and expected output (output). It essentially finds
# the best coefficients (which may be positive or negative) for a*P + b*A + c*output predicting G (gas aperture size).
# It has three functions:
#       -  __init__(self): (public, line) CONSTRUCTOR.
#       -  use_mr(self): (public, line 30) indicates to main program if we can use linear regression or not
#          (based on availability of data).
#       -  collect_data(self): (public, line 45) Collects and prepares data for multiple regression.
#       -  train_and_test(self): (public, line 85): generates multiple regression model, tests it for accuracy.
#       -  predict(self, P, A, output): called by main program to perform prediction.

#---------------------------------------------------------------------------------------------------

# NOTES:   - We use pandas because we want to deal with separate columns of data here.
#          - We will only return valid values in tuple if the r score is higher than set thresholds.
#          - This module offers more sophisticated and accurate prediction than the LR module.

#---------------------------------------------------------------------------------------------------

class MR_predictor:

    # CONSTRUCTOR: we initialise two objects needed for data scaling and multiple regression - both included in sklearn module.
    def __init__(self):
        # Used to perform data scaling through standardisation method.
        self.__scale = StandardScaler()
        # Used to perform actual multiple regression prediction.
        self.__regr = linear_model.LinearRegression()
        # This variable is set to true if the model passes all prediction tests and can make good predictions.
        # False if not.
        self.__model_available = None

    #------------------------------------------------------------------------------------------------

    # USE_LR: This simple function indicates to the main program whether data is available to do
    # multiple regression or not.
    def use_mr(self):
        # check if directory is empty
        if len(os.listdir('ML/data')) == 0:
            return False
        # if not return true.
        return True

    #------------------------------------------------------------------------------------------------

    # COLLECT_DATA: This function iterates through csv files in the data subdirectory and puts all
    # the data together into a single pandas data frame. It then removes duplicate rows, scales the
    # data according to standardisation method and returns the data frames as output.
    def collect_data(self):
        # Define pandas data frame that will accumulate data from csv files.
        accum_df = pd.DataFrame(columns=['# G', 'P', 'A', 'output'])

        # Iterate over files in data directory
        for file in os.listdir('ML/data'):

            # receive data from a csv file into a 4-column padas dataframe.
            filename = 'ML/data/' + str(file)
            new_df = pd.read_csv(filename)

            # concatenate data frame to accumulator data frame defined above
            frames = [accum_df, new_df]
            accum_df = pd.concat(frames, sort = False)

        # remove duplicate rows
        accum_df = pd.DataFrame.drop_duplicates(accum_df)

        # sort out indices in data frame
        accum_df.reset_index(drop=True, inplace=True)

        # Data scaling of X data.
        x_data = accum_df[['P', 'A', 'output']]
        #------------------------OUTPUT STATEMENTS--------------------#
        #print("X DATA: ")
        #print(x_data)
        #print()
        #--------------------------------------------------------------#
        scaled_x_data = self.__scale.fit_transform(x_data)
        #------------------------OUTPUT STATEMENTS--------------------#
        #print("MEAN")
        #print(self.__scale.mean_)
        #print("VARIANCE")
        #print(self.__scale.var_)
        #print("SCALED DATA")
        #print(scaled_x_data)
        #print()
        #--------------------------------------------------------------#

        # the y_data dataframe stores data that will need to be predicted.
        y_data = accum_df['# G']

        # return scaled_x_data, y_data by reference
        return scaled_x_data, y_data

    #------------------------------------------------------------------------------------------------
    # TRAIN_AND_TEST: Split data into training and testing, develop model with training data and then
    # test it.
    def train_and_test(self):
        # Get the data
        x_data, y_data = self.collect_data()

        # 80% of data is for training, 20% is for testing.
        train_x = x_data[:80]
        train_y = y_data[:80]

        test_x = x_data[80:]
        test_y = y_data[80:]

        # Fit training data to multiple regression model.
        self.__regr.fit(train_x, train_y)
        #------------------------OUTPUT STATEMENTS--------------------#
        #print("COEFFS:")
        #print(self.__regr.coef_)
        #print()
        #-------------------------------------------------------------#

        # We can only test the data for correctness if we have enough of it.
        # This is expected to be the case most of the time.
        if len(test_x) > 2:
            # Now make predictions on test x data so that we can test.
            test_prediction = self.__regr.predict(test_x)

            # Compare prediction with the actual values to see how good the model is.
            r2score = r2_score(test_y, test_prediction)

            if r2score > 0.75:
                self.__model_available = True
            else:
                self.__model_available = False
        # If we do not have enough testing data, this means the data is not very complicated so
        # we can skip the testing and just say the model is available.
        else:
            self.__model_available = True

    #------------------------------------------------------------------------------------------------

    def predict(self, P, A, output):

        if self.__model_available is None:
            self.train_and_test()

        if self.__model_available == True:
            scaled_P = (P - self.__scale.mean_[0])/sqrt(self.__scale.var_[0])
            scaled_A = (A - self.__scale.mean_[1])/sqrt(self.__scale.var_[1])
            scaled_output = (output - self.__scale.mean_[2])/sqrt(self.__scale.var_[2])
            data = [[scaled_P, scaled_A, scaled_output]]

            # NOTE: Prediction is a 1 dimensional numpy array.
            prediction = self.__regr.predict(data)
            return prediction[0]
        else:
            return 0.0
