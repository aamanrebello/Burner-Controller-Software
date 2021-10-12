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
        try:
            # Send get request to necessary URL.
            response = requests.get(self.__url + '/initialise')
            # Check result based on status code
            if response.status_code == 200:
                print(response.text)
                return True
            else:
                print("INITIALISATION OF SERVER UNSUCCESFUL. Aborting ML annd sensor data stream.")
                return False
        # If we are unable to connect to the server, return False so that we know
        # not to use ML.
        except requests.exceptions.ConnectionError as c:
            print("UNABLE TO CONNECT TO SERVER. Initialisation failed, aborting ML/data stream.")
            return False

#-----------------------------------------------------------------------------
    # This function is used to check if it is possible to use ML.
    def use_lr(self):
        try:
            # Send get request to necessary URL.
            response = requests.get(self.__url + '/check_ML')
            # Check result based on status code
            print(response.text)
            if response.status_code == 200:
                return True
            else:
                return False
        # If we are unable to connect to the server, return False to handle the error
        except requests.exceptions.ConnectionError as c:
            print("UNABLE TO CONNECT TO SERVER. Check failed, aborting ML.")
            return False

#------------------------------------------------------------------------------
    # This function is used to train the ML models on the server remotely.
    def train_models(self):
        try:
            # Send get request to necessary URL.
            response = requests.get(self.__url + '/train')
            # return of function based on status code
            #---------------------------------------
            # Here, training of LR is successful. Since MR is handled differently,
            # we cannot say if MR has been successfully trained until we call the
            # predict function
            if response.status_code == 200:
                # Store response as dictionary
                coeffs = response.json()
                # The last return value indicates whether the model should be used.
                return coeffs['LR_m'], coeffs['LR_c'], True
            # Here the model generated was not accurate enough.
            else:
                print(response.text)
                return 0, 0, False
        # If we are unable to connect to the server, return False to handle the error
        except requests.exceptions.ConnectionError as c:
            print("UNABLE TO CONNECT TO SERVER. Training failed, aborting ML.")
            return 0, 0, False

#-------------------------------------------------------------------------------
    # This function is used to obtain the multiple regression prediction from the remote server.
    def predict(self, P, A, output):
        try:
            # Prepare data for POST request.
            readings = {
                "supply_pressure": P,
                "air_aperture": A,
                "output": output
            }
            # Send POST request to necessary URL.
            response = requests.post(self.__url + '/MR_predict', json = readings)
            # return of function based on status code
            if response.status_code == 200:
                return float(response.text)
            else:
                print("PREDICTION UNSUCESSFUL - server side exception")
                return 0.0
        # If we are unable to connect to the server, return 0.0 to handle the error
        # 0.0 will not be accepted by the main system.
        except requests.exceptions.ConnectionError as c:
            print("UNABLE TO CONNECT TO SERVER. Prediction failed.")
            return 0.0

#-------------------------------------------------------------------------------
    # This function sends sensor readings to the server to be saved there as a csv.
    def send_readings(self, G, P, A, output):
        try:
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
            if response.status_code == 200:
                return True
            else:
                print("Data send unsuccesful - server side exception.")
                return False
        # If we are unable to connect to the server, return False to handle the error
        except requests.exceptions.ConnectionError as c:
            print("UNABLE TO CONNECT TO SERVER. Unable to send current data.")
            return False

#-------------------------------------------------------------------------------
    def end_data(self, filename='labelled_data'):
        try:
            # Send get request to necessary URL.
            print('URL: ' + self.__url + '/finishdata/' + filename)
            response = requests.get(self.__url + '/finishdata/' + filename)
            # Check result based on status code
            if response.status_code == 200:
                print("DATA STREAM CLOSED.")
                return True
            else:
                print("DATA STREAM CLOSE UNSUCESSFUL - Server side exception will be rectified.")
                return False
        # If we are unable to connect to the server, return False to handle the error
        except requests.exceptions.ConnectionError as c:
            print("UNABLE TO CONNECT TO SERVER. Unable to end data stream, matter will be rectified.")
            return False

#--------------------------------------------------------------------------------
# END
