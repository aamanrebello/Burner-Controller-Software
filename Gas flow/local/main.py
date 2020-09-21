from memory_prediction.memory_predictor import memory_predictor
from ML.multiple_regression import MR_predictor
from ML.linear_regression import LR_predictor
import testing.reading_generator as r_g

import numpy as np
import time

# DOCUMENTATION: Central program which coordinates the various programs in the project (memory based,
# ML based, actuator communication). Loops for a set period of time every day. During an iteration,
# utilises outputs from ML-based and memory-based position calculation. Updates CSV file to provide
# labelled data to the ML program.
#
# Below there is also a 'search' functionn which is used to ensure that data in the LRU cache is not repeated
# (before adding data to tne cache, the cache is searched to make sure the data is not already there)

#-----------------------------------------------------------------------------------------------------

# NOTES: - Data is accumulated in a numpy array over the course of looping and is written at the end. This
#          avoids overhead due to open files, or bad effects of failure to write to file at some point in
#          the looping.
#
#        - If the cache is not at full capacity, new data is appended to it. If it is at full capacity, the least
#          recently used data is discarded, all elements are shifted one place to the right and the new data is
#          inserted in the beginning indices.
#
#        - This component is likely to communicate with sensors and other processing devices through other
#          Python modules.
#
#        - If the required output value changes at any time, then for these iterations only we will use linear regression
#          to get faster convergence. In all other cases we will use memory prediction.
#
#        - However, if memory prediction does not generate a result after a set threshold of tries, we use multiple
#          regression as a last resort.

#------------------------------------------------------------------------------------------------------

def main():
    # Set number of iterations
    count = 165

    # Initialise numpy array. This array records all the data extracted from the sensors so that it can
    # be used by the ML modules to make predictions.
    MLdata = np.array([[], [], [], []])

    # Initialise another numpy array.
    cache = np.array([[], [], [], []])

    #define maximum size of above data structure to limit memory usage
    MAX_SIZE = 100

    #define threshold of misses before we need to use multiple regression.
    MISS_THRESHOLD = 8

    # INDEX 0 - absolute position of actuator (gas aperture size) is the first array in cache
    # INDEX 1 - measured fuel gas supply pressure is the second array in cache
    # INDEX 2 - air aperture size is the third array in cache
    # INDEX 3 - corresponding output value is third array in cache
    GAS_APERTURE, PRESSURE, AIR_APERTURE, OUTPUT = 0, 1, 2, 3

    #------------------------------------------------------------------------------------------------

    # Instantiate object of memory_predictor class.
    m_p = memory_predictor()
    # Instantiate object of LR_predictor class (linear regression).
    lr_p = LR_predictor()
    # Instantiate object of MR_predictor class (multiple regression).
    mr_p = MR_predictor()

    #------------------------------------------------------------------------------------------------

    # The use_lr function indicates if it is possible to use ML, based on availability of data
    use_ML = lr_p.use_lr()
    #use_ML = False

    #----------------------------------------------------------------------------------------------

    # TODO - train ML model(s) if use_ML is true - obtain coefficients m and c
    if use_ML:
        LR_m, LR_c = lr_p.find_line()
        mr_p.train_and_test()

    #----------------------------------------------------------------------------------------------

    # Define time delay in seconds between successive loop iterations
    DELAY = 0.5

    # Define variable to hold number of iterations
    iterations = 0

    # Define variable to record number of misses when using memory prediction.
    misses = 0

    # Define variable to hold required output of system. In the loop below, we will also need to record
    # the required output on the previous iteration as we compare the two to determine if we use ML or not.
    required_output = 0
    old_required_output = 0

    # Define initial gas aperture. It must be closed (off) to begin with, so 0
    gas_aperture = 0

    while iterations < count:

        # Receive Sensor Data
        sensordata = r_g.return_reading(iterations*DELAY, gas_aperture)

        # If the device is off, we do not need to continue with the remaining contents of the loop.
        if not sensordata['on']:
            print("switched off.")
            # we keep the delay and iterations to keep track of the passage of time.
            iterations += 1
            time.sleep(DELAY)
            continue

        supply_pressure = sensordata['supply_pressure']
        air_aperture = sensordata['air_aperture']
        current_output = sensordata['current_output']

        # recieve data into 4x1 numpy array
        newdata = np.array([[gas_aperture], [supply_pressure], [air_aperture], [current_output]])

        # we need to record the old value of required output so that we can compare with the new value.
        # if the values are different, when we compare, we will use ML.
        if iterations > 0:
            old_required_output = required_output
        # receive new required output value
        required_output = sensordata['required_output']

    #---------------------------------------------------------------------------------------------------------------------------------
        # Now we have to add the received data values to our cache. If the current size of the subarrays in the cache is less
        # than the maximum allowed size, we append the data to the end of the numpy array, increasing the size. If maximum size is
        # reached, replace the last value with our new data. In both cases, the data added to the end will be moved to the beginning when
        # we call the memory_predict function (from which we call the shuffle function to do this).

        # First check if the received data already exists in the cache
        index = search(cache, newdata)

        # In case there is no repeat
        if index == -1:

            # Case 1: Size of subarrays in cache < maximum allowed Size
            # - we just add the new element at the beginning, increasing the array size
            if len(cache[OUTPUT]) < MAX_SIZE:
                # concatenate newdata with cache, row wise
                cache = np.concatenate((newdata, cache), axis = 1)

            # Case 2: Size equals maximum allowed size
            # - we insert new data at the end, replacing LRU data.
            else:
                cache[OUTPUT, MAX_SIZE - 1] = newdata[OUTPUT, 0]
                cache[AIR_APERTURE, MAX_SIZE - 1] = newdata[AIR_APERTURE, 0]
                cache[PRESSURE, MAX_SIZE - 1] = newdata[PRESSURE, 0]
                cache[GAS_APERTURE, MAX_SIZE - 1] = newdata[GAS_APERTURE, 0]

                # then we shuffle the newly added data to the beginning
                m_p.shuffle(cache, MAX_SIZE - 1)

        # In case there is repeated data, we need only shuffle this repeated data back to the beginning
        else:
            m_p.shuffle(cache, index)

    #--------------------------------------------------------------------------------------------------------------------------------------------

        # Next we have to update the MLdata with the newly received data (if it is not repeated)
        if search(MLdata, newdata) == -1:
            # concatenate MLdata with newdata, row wise - no need to shuffle
            MLdata = np.concatenate((MLdata, newdata), axis = 1)

    #---------------------------------------------------------------------------------------------------------------------------------------------
        # make predictions
        # if ML is available and there is a change in required output, we will use the ML to make a prediction.
        # Note required_output = LR_m*supply_pressure*air_aperture*gas_aperture/100000 + LR_c. We want to find gas_aperture.
        if use_ML and required_output != old_required_output:
            new_aperture = ((required_output - LR_c)*100000)/(LR_m*supply_pressure*air_aperture)

            # round to 2 and check that prediction falls in valid range
            if new_aperture >= 0 and new_aperture <= 100:
                print("LR ADJUSTMENT: " + str(new_aperture - gas_aperture))
                gas_aperture = round(new_aperture, 2)
            else:
                print("LR ADJUSTMENT ABORTED - OUT OF RANGE VALUE")

        # If the miss threshold is breached we use multiple regression as a last resort.
        elif use_ML and misses >= MISS_THRESHOLD:
            new_aperture = mr_p.predict(supply_pressure, air_aperture, required_output)
            misses = 0

            if new_aperture >= 0 and new_aperture <= 100:
                print("MR ADJUSTMENT: " + str(new_aperture - gas_aperture))
                gas_aperture = round(new_aperture, 2)
            else:
                print("MR ADJUSTMENT ABORTED - OUT OF RANGE VALUE")

        # else we use memory prediction.
        else:
            context = {
                        'gas_aperture': gas_aperture,
                        'supply_pressure': supply_pressure,
                        'air_aperture': air_aperture,
                        'current_output': current_output
            }

            # if the adjustment is non-zero, then this means it is a miss and we need to update misses.
            adjustment = m_p.actuator_predict(context, required_output, cache)
            if adjustment == 0:
                misses = 0
            else:
                misses += 1
            gas_aperture += adjustment
            #round to two decimal places
            gas_aperture = round(gas_aperture, 2)

        print("iteration: " + str(iterations) + ", gas_aperture: " + str(gas_aperture))
        # increment count
        iterations += 1

        # programmed DELAY
        time.sleep(DELAY)

    # save numpy array as csv file in Ml/data location
    MLdata = MLdata.T
    np.savetxt("ML/data/labelled_data.csv", MLdata, delimiter = ',', header = 'G,P,A,output')

    # zero return code indicates successful completion
    return 0



#--------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------

#####VERIFIED#####
# (Some more testing before removing output statements)

# NOTES ON SEARCH FUNCTION: - Function takes two parameters - arr : the 2 dimensional array to be searched & check: a 4x1 matrix
#                             which we want to check exists in arr.
#                           - we essentially need to find instances in which data values in the rows of the numpy array are all
#                             the same.
#                           - if only one parameter is different, we would need to change this parameter to the new value.
#                           - the function returns the index of the repeated data. Else it returns -1.
#                           - It takes two parameters - the numpy array to be searched and another numpy array containing
#                             the parameters to be checked

#---------------------------------------------------------------------------------------------------------------------------------------------------

def search(arr, check):

    for i in range(0, len(arr[0])):
        # First check if output values in row 3 are the same
        if check[3, 0] == arr[3, i]:
            # Next check other parameters
            matching_parameters = 0
            for j in range(0, 3):
                if check[j, 0] == arr[j, i]:
                    matching_parameters += 1

            # in case of a perfect match
            if matching_parameters == 3:
                return i

            # in case only one parameter is different, we have to replace the values
            elif matching_parameters == 2:
                arr[0, i] = check[0, 0]
                arr[1, i] = check[1, 0]
                arr[2, i] = check[2, 0]
                return i

    # else return -1
    return -1


#------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------

# Declare main() as the main function
if __name__ == "__main__":
    import sys
    ret=main()
    sys.exit(ret)
