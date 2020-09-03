import numpy as np

#####VERIFIED#####

# MEMORY_PREDICTOR: This class is intended to predict the reauired fuel gas aperture size (i.e. actuator position) for
# a given required output with the help of an LRU cache (implemented with a numpy array). It has 3 functions:

#   - __init(self)__ : (line 25) Constructor.

#   - actuator_predict(self, context, req_output, data): (public, line 32): Performs the actual prediction and cache manipulation

#   - shuffle(self, data, index): (public, line 180): Helper function for manipulating cache.

#---------------------------------------------------------------------------------------------------------------------

# NOTES: - Aperture size (for both air and fuel) is provided as a value between 0 (fully closed) and 100 (fully open).

#        - It is assumed that the only controllable parameter is the size of the aperture allowing fuel gas to enter
#          the burner.

#        - No sudden changes are expected in the other parameters. They will be flagged in the main program if there is
#          sudden change/ they fall below a particular threshold value.

#--------------------------------------------------------------------------------------------------------------------

class memory_predictor:

#--------------------------------------------------------------------------------------------------------------------
    # CONSTRUCTOR : There are no instance variables to initialise.
    def __init__(self):
        pass


#--------------------------------------------------------------------------------------------------------------------

    # ACTUATOR PREDICTOR: function receives required output value (req_output), current contextual values
    # (context, containing supply pressure, air aperture size, and fuel gas aperture size controlled by actuator)
    # and the LRU cache (data - a 4 row numpy array with max 1000 columns) by reference and returns required
    # adjustment of the size of the aperture supplying fuel gas by searching the cache. Required accuracy in output
    # is 5%. In case there isn't a good enough match, linear extrapolation is employed between the two nearest
    # guesses (upper and lower) in the cache.
    def actuator_predict(self, context, req_output, data):

        # INDEX 0 - absolute position of actuator (gas aperture size) is the first array in cache
        # INDEX 1 - measured fuel gas supply pressure is the second array in cache
        # INDEX 2 - air aperture size is the third array in cache
        # INDEX 3 - corresponding output value is third array in cache
        GAS_APERTURE, PRESSURE, AIR_APERTURE, OUTPUT = 0, 1, 2, 3

        #define maximum size of above data structures to limit memory usage
        MAX_SIZE = 1000

        #we know required accuracy in fuel apeture and other readings is 5% and set it as below:
        FUEL_ACCURACY = 0.05
        READING_ACCURACY = 0.05

        # store values of context in variables for ease:
        gas_aperture = context['gas_aperture']
        supply_pressure = context['supply_pressure']
        air_aperture = context['air_aperture']

        current_output = context['current_output']
    #-----------------------------------------------------------------------------------------
        # First, we will check if the output value falls in the required range, and if so indicate no adjustment is needed.
        if abs(current_output - req_output)/req_output < FUEL_ACCURACY:
            print("value found")
            return 0

        #---------------------------------------------------------------------------
        # If not, we iterate over OUTPUT row in the numpy array to find if a close enough approximation to the
        # required output exists. To do this, we find the stored positions of actuator that will give closest
        # approximation of output - upper and lower bound. If the closest of these two falls within the required
        # accuracy, then this is the position we return.
        # Else, we assume a linear scale between upper and lower bound to calculate required actuator position

        # If no values are stored in the array, the upper and lower bound of position will be 100 and 0 respectively.
        max_position, min_position = 100, 0

        # We set bounds on the output. We select a large value for the output that will not ever be surpassed.
        output_upper_bound, output_lower_bound = 1000000, 0

        # We want indices of the upper and lower bounds of position/output. -1 at the end of all iterations
        # indicates that the data structure currently has no data.
        upper_bound_index, lower_bound_index = -1, -1

        # we store the error of our best estimate in 'out_error'. We initialise it to 'req_output' as this is the maximum possible value
        # it can hold.
        out_error = req_output

        # iterate over elements in data structure
        for i in range(0, len(data[OUTPUT])):
            # find errors in data structure values wrt input parameters
            pressure_error = abs(data[PRESSURE, i] - supply_pressure)
            air_error = abs(data[AIR_APERTURE, i] - air_aperture)

            # first check if measured conditions are similar
            if pressure_error/supply_pressure < READING_ACCURACY and air_error/air_aperture < READING_ACCURACY:

                #---------------------------------------
                # Set index of best upper bound
                if data[OUTPUT, i] > req_output and data[OUTPUT, i] < output_upper_bound:
                    output_upper_bound = data[OUTPUT, i]
                    upper_bound_index = i
                #----------------------------------------
                # Set index of best lower bound
                elif data[OUTPUT, i] < req_output and data[OUTPUT, i] > output_lower_bound:
                    output_lower_bound = data[OUTPUT, i]
                    lower_bound_index = i

        # at this point, we have the lower and upper bounds. We initialise upper and lower bound errors to ridiculously large
        # values so that in case the data structure is empty we will go into case 3 below.
        upper_bound_error, lower_bound_error = 100000, 100000

        # in case the data structure is not empty, upper/lower bound index > 0 and we will have an estimate to work with.
        if upper_bound_index >= 0:
            upper_bound_error = abs(data[OUTPUT, upper_bound_index] - req_output)

        if lower_bound_index >= 0:
            lower_bound_error = abs(data[OUTPUT, lower_bound_index] - req_output)

        req_position = 0 # initialise variable to be used later - represents required actuator position.
        #----------------------------------------------------

        #CASE 1: DATA STRUCTURE HAS A "CLOSE ENOUGH" ESTIMATE AND THE UPPER BOUND IS CLOSEST
        if upper_bound_error/req_output < FUEL_ACCURACY and upper_bound_error < lower_bound_error:
            #store required position and flow rate in variables (prepare to reshuffle data structures)
            req_position = data[GAS_APERTURE, upper_bound_index]
            #call shuffle function defined below to ensure we follow the LRU algorithm
            self.shuffle(data, upper_bound_index)
        #----------------------------------------------------

        #CASE 2: DATA STRUCTURE HAS A "CLOSE ENOUGH" ESTIMATE AND THE LOWER BOUND IS CLOSEST
        elif lower_bound_error/req_output < FUEL_ACCURACY:
            #store required position and flow rate in variables (prepare to reshuffle data structures)
            req_position = data[GAS_APERTURE, lower_bound_index]
            #call shuffle function defined below to ensure we follow the LRU algorithm
            self.shuffle(data, lower_bound_index)
        #----------------------------------------------------

        #CASE 3: DATA STRUCTURE DOES NOT HAVE A GOOD ENOUGH ESTIMATE
        else:
            if upper_bound_index >= 0:
                max_position = data[GAS_APERTURE, upper_bound_index]
                # Call shuffle function to ensure we follow the LRU algorithm.
                self.shuffle(data, upper_bound_index)

            # since we shuffled we may need to add 1 to the lower bound index to
            # ensure it points to the same required values
            if lower_bound_index >= 0 and lower_bound_index < upper_bound_index:
                lower_bound_index += 1

            if lower_bound_index >= 0:
                min_position = data[GAS_APERTURE, lower_bound_index]
                # Call shuffle function to ensure we follow the LRU algorithm.
                self.shuffle(data, lower_bound_index)

            # We estimate the required position of actuator by assuming a linear relationship with gas aperture
            # between upper and lower bound points.
            if upper_bound_index >= 0 and lower_bound_index >= 0:
                numerator = (lower_bound_error*max_position + upper_bound_error*min_position)
                denominator = (upper_bound_error + lower_bound_error)
                req_position = numerator/denominator

            # however if one or both of the points does not exist, we just take the average of our
            # upper and lower limit positions.
            else:
                req_position = (max_position + min_position)/2
    #-------------------------------------------------------------------------------

        # return adjustment rounded to two decimal places (required return result same in either case)
        adjustment = req_position - gas_aperture
        print("ADJUSTMENT: " + str(adjustment))
        return round(adjustment, 2)

#--------------------------------------------------------------------------------------------------------------------

    # SHUFFLE: Function used to shuffle sub-arrays in data structure. It is called in actuator_predict
    # to help implement the LRU algorithm. Given a 2-dimensional numpy array (data) and a positive index
    # (index), it moves the element at this index to position zero in each sub-array. The elements having
    # index lower than the provided index in each list are all "shifted to the right" to fill up the
    # "gaps" left by the selected elements that have been moved out in each sub-array.

    def shuffle(self, data, index):
        #terminate function in case of invalid index
        if index >= len(data[0]):
            return -1

        # Shuffle each list, one by one
        for subarray in data:
            # Temporarily store element at the provided index
            selected_element = subarray[index]

            #shuffle elements before index in the list along one step to the right
            for i in range(index-1, -1, -1):
                subarray[i+1] = subarray[i]

            #replace first element with required values (so that most recently used comes first)
            subarray[0] = selected_element

        # return zero means the shuffle was successful
        return 0

#-----------------------------------------------------------------------------------------------------------------
# END OF CLASS #
