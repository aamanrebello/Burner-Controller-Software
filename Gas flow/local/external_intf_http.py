import requests

# This class is used to send data to the server that runs the ML programs. This is
# done via HTTP requests (GET, POST etc.). This program receives responses back and
# and provides them back to the main program in the required format.

#-------------------------------------------------------------------------------------

class external_interface:

#----------------------------------------------------------------------------
    # Define constructor (We initialise object with base URL of server)
    # Default value is port 5003 on localhost (for testing)
    def __init__(self, url='http://127.0.0.1:8000'):
        self.__url = url

#------------------------------------------------------------------------------
    # Initialise communciation with server.
    def initialise(self):
        # Send get request to necessary URL.
        response = requests.get(self.__url + '/initialise')
        # Check result based on status code
        if response.status_code == 200:
            return True
        else:
            return False

#-----------------------------------------------------------------------------
    # This function is used to check if it is possible to use ML.
    def use_lr(self):
        # Send get request to necessary URL.
        print('URL: ' + self.__url + '/check_ML')
        response = requests.get(self.__url + '/check_ML')
        # Check result based on status code
        print("STATUS CODE - " + str(response.status_code))
        if response.status_code == 200:
            return True
        else:
            return False

#------------------------------------------------------------------------------
    # This function is used to train the ML models on the server remotely.
    def train_models(self):
        # Send get request to necessary URL.
        response = requests.get(self.__url + '/train')
        # return of function based on status code
        print("STATUS CODE - " + str(response.status_code))
        if response.status_code == 200:
            # Store response as dictionary
            coeffs = response.json()
            return coeffs['LR_m'], coeffs['LR_c']
        else:
            return 0, 0

#-------------------------------------------------------------------------------
    # This function is used to obtain the multiple regression prediction from the remote server.
    def predict(self, P, A, output):
        # Prepare data for POST request.
        readings = {
            "supply_pressure": P,
            "air_aperture": A,
            "output": output
        }
        # Send POST request to necessary URL.
        response = requests.post(self.__url + '/MR_predict', json = readings)
        # return of function based on status code
        print("STATUS CODE - " + str(response.status_code))
        if response.status_code == 200:
            print("PREDICT RESPONSE: " + response.text)
            return float(response.text)
        else:
            return 0.0

#-------------------------------------------------------------------------------
    # This function sends sensor readings to the server to be saved there as a csv.
    def send_readings(self, G, P, A, output):
        # Prepare data for POST request.
        readings = {
            "supply_pressure": P,
            "air_aperture": A,
            "gas_aperture": G,
            "output": output
        }
        # Send POST request to necessary URL.
        response = requests.post(self.__url + '/newdata', json = readings)
        # return of function based on status code
        print("STATUS CODE - " + str(response.status_code))
        if response.status_code == 200:
            return True
        else:
            return False

#-------------------------------------------------------------------------------
    def end_data(self, filename='labelled_data'):
        # Send get request to necessary URL.
        print('URL: ' + self.__url + '/finishdata/' + filename)
        response = requests.get(self.__url + '/finishdata/' + filename)
        # Check result based on status code
        # Check result based on status code
        print("STATUS CODE - " + str(response.status_code))
        if response.status_code == 200:
            return True
        else:
            return False
#--------------------------------------------------------------------------------
# END
