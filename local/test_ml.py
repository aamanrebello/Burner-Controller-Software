from ML.multiple_regression import MR_predictor
from ML.linear_regression import LR_predictor
from testing.test_environment import test_environment

# This script is designed to analyse the effectiveness of ML algorithms - linear regression and
# multiple regression. The user provides P, A, G, output values from the command line and then a prediction
# is made with the selected algorithm (LR or MR). This is then compared with the actual value as provided by the
# test environment and a precentage difference is also provided.

# This variable determines whether we are using multiple regression (set to true) or not (set to false).
use_mr = True

# Since we are directly using the test environment, we need to specify the model number we want.
MODEL_NUMBER = 2
# Create test environment object
t_e = test_environment(MODEL_NUMBER)

# We only break the loop when user indicates that no more inputs are necessary.
while True:

    # Receive user input
    P = float(input("Enter pressure in Pascal: "))
    A = float(input("Enter air aperture on scale 0 to 100: "))
    required_output = float(input("Enter the required output in kelvin: "))

    # Initialise these variables to zero for now.
    obtained_output = 0
    predicted_G = 0

    if use_mr:
        mr_p = MR_predictor()
        mr_p.train_and_test()
        predicted_G = mr_p.predict(P, A, required_output)
        print(type(predicted_G))

    else:
        lr_p = LR_predictor()
        LR_m, LR_c = lr_p.find_line()

        predicted_G = ((required_output - LR_c)*100000)/(LR_m*P*A)

    #based on the predicted value of G, find the corresponding output.
    obtained_output = t_e.retrieve_out_val(P, A, predicted_G)
    print("OBTAINED OUTPUT: " + str(obtained_output))

    # Find and output percentage difference
    perc_df = (obtained_output - required_output)*100/required_output
    print("PERCENTAGE DIFFERENCE: " + str(perc_df))

    print()

    # User can specify if he wants another value to be tested or to end testing.
    next = input("Do you want to continue? (Y/N): ")
    if next != "Y":
        break
