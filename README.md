# Fuel Gas Controller Software

This software, written in Python, controls the temperature of a gas burner based on what the user desires. It is designed for the below plan:

![Personal-project-plan](https://user-images.githubusercontent.com/56508438/136956580-e1b0028a-bc73-47b7-88de-ea3694a34a9e.PNG)


The code in the folder [*local*](local) is meant to run on the local device. It contains the memory caching algorithm and directly provides adjustment 
recommendations to the local actuator. Currently, because we do not have access to hardware yet, a software testing framework has been created in *local* [here](local/testing) 
which we can use to test the recommendations. The testing framework can assume different kinds of relationships between the parameters P, A, G and T (refer to the diagram).

The code in folder [*Remote*](remote) runs on the remote server. It is built using the [Flask](https://flask.palletsprojects.com/en/2.0.x/) framework.
The [*ML*](Remote/ML) folder has ML algorithms - we can add more here, but at present it has univariate and multivariate linear regression. It recieves data from
the local device over a stateful HTTP interface and stores it in a CSV file for analysis. Libraries used for machine learning are SciPy, Sckikit-learn, NumPy and Pandas.


## How to Run

The software can be run against the testing framework. To just run the local device software, starting from [*local*](local) directory do: 
```
python main.py
```
This will run the program for a fixed amount of iterations, outputting results to the console. Each iteration is 5 seconds in length.

To also involve the server, starting from [*Remote*](remote) directory run separately:
```
python external_intf_http.py
```
This will set up the server to listen. Then when you run the local program, the server will recieve data and if it has data to learn from, may even contribute its own predictions.


### Adjusting the testing:
You can modify the [schedule](local/testing/schedule.csv) here. This specifies all the parameters plus the user's desired temperature. It also specifies 
how long these conditions last under the 'time' column.

You can also add new models to [the environment](local/testing/test_environment.py). To use a particular model, adjust the value of `MODEL_NUMBER` in the 
[reading generator](local/testing/reading_generator.py).

### Adjusting servers:
Currently we do not use any lookup resolution to find the remote server. You need to specify the remote server address in local [here](local/main.py#L55).

The author intends to extend this software in the future at a suitable time.
