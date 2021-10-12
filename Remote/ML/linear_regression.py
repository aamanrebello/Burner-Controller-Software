import numpy as np
import os
from scipy import stats

# LR_PREDICTOR: This class collects data stored by sensors from the csv files, preprocesses
# them by removing duplicates from the numpy array, then develops a predictive model based
# on the data, using linear regression. It has three functions:

    # - __init__(self): (public, line 23) CONSTRUCTOR.
    # - use_lr(self): (public, line 30) indicates to main program if we can use linear regression or not
    #                 (availability of data).
    # - collect_data(self): (public, line 45) Collects and prepares data for linear regression.
    # - find_line(self): (public, 85): generates linear regression model, returns coefficients.

#---------------------------------------------------------------------------------------------------

# NOTES: - This module essentially finds the line of best fit for the data i.e. given a line
#          y = mx + c, where x = P*A*G (P = supply pressure, A = air aperture, G = fuel gas aperture)
#          it determines the m and c that have the lowest average error with respect
#          to the data points and returns a tuple (m, c) for use in the main program.
#        - We will only return valid values in tuple if the standard error/ other parameters are
#          higher/lower than set thresholds

#---------------------------------------------------------------------------------------------------
class LR_predictor:

    # CONSTRUCTOR: we have no member variables to initialise.
    def __init__(self):
        pass

    #------------------------------------------------------------------------------------------------

    # USE_LR: This simple function indicates to the main program whether data is available to do
    # Linear regression or not.
    def use_lr(self):
        # check if directory is empty
        if len(os.listdir('ML/data')) == 0:
            return False
        # if not return true.
        return True

    #-------------------------------------------------------------------------------------------------


    # COLLECT_DATA: This function iterates through csv files in the data subdirectory and puts all
    # the data together into a single numpy array. It then removes duplicate columns from this array
    # and returns it by reference.
    def collect_data(self):
        # Define numpy array that will store data from csv files.
        accumulator = np.empty(shape=(1,4))

        # Iterate over files in data directory
        for file in os.listdir('ML/data'):

            # receive data from a csv file into a 4-column numpy array
            filename = 'ML/data/' + str(file)
            newdata = np.genfromtxt(filename, delimiter = ',')

            # append numpy array to accumulator defined above
            accumulator = np.concatenate((accumulator, newdata), axis = 0)

        # note that in the beginning we declared accumulator as an empty matrix,
        # so now there will be an unwanted row of zeroes at the top of our
        # matrix. We get rid of it here.
        accumulator = np.delete(accumulator, (0), axis=0)
        # remove duplicate rows
        accumulator = np.unique(accumulator, axis = 0)
        # now take transpose for next step (i.e. column now become rows: 4xn)
        accumulator = accumulator.T

        # note that the P*A*G product is very large so we need to scale it down by dividing by a constant fixed value
        SCALING_FACTOR = 100000
        # initialise numpy array to store scaled product P*A*G for each column in accumulator array
        x_data = np.zeros(len(accumulator[0]))
        # fill up values
        for i in range(0, len(accumulator[0])):
            x_data[i] = accumulator[0, i]*(accumulator[1, i]/SCALING_FACTOR)*accumulator[2, i]

        # initialise numpy array to store values corresponding to P*A*G product
        y_data = np.array(accumulator[3])

        # return x_data, y_data by reference
        return x_data, y_data

    #---------------------------------------------------------------------------------------------------------------

    # FIND_LINE: This function takes in the x data and y data and develops a linear regression model using scipy. It returns
    # a tuple (m, c) where y = mx + c. This is subject to the standard error and coefficient of correlation being below and above
    # certain threshold values respectively.
    def find_line(self):

        x_data, y_data = self.collect_data()

        slope, intercept, coeff_of_correlation, pvalue, std_error = stats.linregress(x_data, y_data)

        # we need to check that there is reasonable correlation between x_data and y_data
        if coeff_of_correlation > 0.7 and std_error < 5:
            return slope, intercept

        return 0, 0

    #-----------------------------------------------------------------------------------------------------------------
