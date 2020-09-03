from testing.test_environment import test_environment

import numpy as np

# DOCUMENTATION: Based on provided values of required output value, supply pressure and air aperture size, this
# module generates the current output value given the actuator position indicated by our predictor. It does this
# by passing these values as parameters to one of the models from the test environment and retrieving the output
# value. In effect, this allows us to test out our predictor by creating a "mock" interactive environment.

# We have two functions:
#           - return_reading(time, gas_aperture) : reads an input file where the required output value,
#             supply pressure and air aperture size are specified for all time instants. Assimilates this
#             information then calls the function below to obtain the corresponding output value at the
#             provided time. The function receives two parameters -
#
#           - retrieve_out_val(P, A, G, modelno) : passes as parameters supply pressure (P), air aperture size (A),
#             and fuel gas aperture size (G) and the required model from the test environment. Returns the output
#             value associated with these parameters, based on the model.
#

#---------------------------------------------------------------------------------------------------------------------------

# NOTES: - The input file used in return_reading is a csv file called 'schedule.csv'. This has 4 columns -
#          required output, supply pressure, air aperture size, and time (in seconds) for which these settings apply.
#        - The return reading function will read the csv file into a numpy array and analyse the array to determine the parameter
#          values for the current time instant. It then returns these parameters as a dictionary.
#        - This is not an optimal method but will be ok for testing purposes.

#---------------------------------------------------------------------------------------------------------------------------

def return_reading(time, gas_aperture):

    # configurable parameter: model number from test environment
    MODEL_NUMBER = 3

    # instantiate object of test environment
    t_e = test_environment(MODEL_NUMBER)

    # configurable parameter: csv file from where we read testing schedule
    FILENAME = 'testing/schedule.csv'

    # read csv file into numpy array
    schedule = np.genfromtxt(FILENAME, delimiter = ',', skip_header = 1)

    # define variable to determine current time instant
    total = 0
    array_row = 0

    while total < time:
        # if we exhaust all rows in csv file, indicate this by returning an empty array
        if array_row == np.shape(schedule)[0]:
            return {}

        total += schedule[array_row, 3]
        array_row += 1

    # when we exit the loop we have the required row of the numpy array + 1 stored in array_row.
    # so we can therefore take the parameters from there.
    array_row -= 1

    # first we need to determine if the controlled device is on/off, which we can tell if the
    # required output <= 20 i.e. less than or equal to room temperature.
    required_output = schedule[array_row, 0]
    on = required_output > 20

    # then other parameters.
    P = schedule[array_row, 1]
    A = schedule[array_row, 2]
    current_output = t_e.retrieve_out_val(P, A, gas_aperture)

    readings = {
                    'on': on,
                    'supply_pressure': P,
                    'air_aperture': A,
                    'current_output': current_output,
                    'required_output': required_output
    }

    return readings

#------------------------------------------------------------------------------------------------------------------------------
