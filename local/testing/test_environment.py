import math

##### VERIFIED ######

# TEST_ENVIRONMENT: This class is part of the testing system that is used to verify that the predictor works.
# It generates output values for different values of the input parameters (P - pressure, A - air aperture size,
# G - fuel gas aperture size) based on different models that are implemented in various private member functions.
# It has one member variable:

#   - __model_no (private): Used to select on instantiation of the object which model function we will use.

# It has 6 member methods:

#   - __model1(self, P, A, G): (private, line 34): Linear relationship with P*A*G of the form y = mx + c - (REALISTIC MODEL)
#   - __model2(self, P, A, G): (private, line 41): Like 1, but coefficients of the linear relationship (m and c) vary with
#                                                different values of P and T. - (REALISTIC MODEL)
#   - __model3(self, P, A, G): (private, line 124): Like 1, but linear relationship is with sqrt(P*G)*A.
#   - __model4(self, P, A, G): (private, line 143): Like 2, but the linear relationship is with sqrt(P*G)*A
#   - __model5(self, P, A, G): (private, line 206): flow rate = a*P + b*A + c*G
#   - retrieve_out_val(self, P, A, G): (public, line 226): Function used by external programs to obtain values ot output from the
#                                                           environment given parameters P, A and G.

# --------------------------------------------------------------------------------------------------------------

# NOTES: - Each function will recieve the parameters P, A, G and return the flow rate based on the model.
#        - Pressure in Pa, Aperture area (both) in value between 0 and 100 representing percentage of
#          area available.

#--------------------------------------------------------------------------------------------------------------

class test_environment:

#--------------------------------------------------------------------------------------------------------------
    # CONSTRUCTOR: Class has one private member variable - model_no. This is an integer which is
    # used to determine which of the below model functions we will be using.
    def __init__(self, model_no):
        self.__model_no = model_no

#---------------------------------------------------------------------------------------------------------------

    # MODEL 1 (private): Linear relationship with P*A*G of the form y = mx + c - (REALISTIC MODEL)
    def __model1(self, P, A, G):
        # first define c in y = mx + c
        c = 0.232
        # next define m
        m = 0.000013

        # next define output as per model
        output = m*P*A*G + c

        # output temperature cannot be below room temperature
        if output < 20:
            output = 20

        # we round to 2 decimal places and return
        return round(output, 2)

#---------------------------------------------------------------------------------------------------------------

    # MODEL 2 (private): Linear relationship with P*A*G of the form y = mx + c, but coefficients of the linear
    # relationship (m and c) vary with different values of P and T. - (REALISTIC MODEL)
    def __model2(self, P, A, G):
        # TODO: Set Parameters based on temperature and pressure ranges
        # P < 5000
        if P < 5000:
            # A < 30
            if A < 30:
                m, c = 0.000005, 4.3
            # 30 <= A < 75
            elif A < 75:
                m, c = 0.0000059, 3.1
            # 75 <= A <= 100
            else:
                m, c = 0.0000073, 0

        # 5000 <= P < 15000
        elif P < 15000:
            #  A < 35
            if A < 35:
                m, c = 0.000004, 3.9
            # 35 <= A < 77
            elif A < 77:
                m, c = 0.0000045, 3.2
            # 77 <= A <= 100
            else:
                m, c = 0.0000055, 0

        # 15000 <= P < 35000
        elif P < 35000:
            # A < 40
            if A < 40:
                m, c = 0.0000035, 3.5
            # 40 <= A < 80
            elif A < 80:
                m, c = 0.0000039, 3
            # 80 <= A
            else:
                m, c = 0.0000044, 0

        # P >= 35000
        else:
            # A < 300
            if A < 42:
                m, c = 0.000003, 3
            # 300 <= A < 700
            elif A < 85:
                m, c = 0.0000033, 2.8
            # 700 <= A
            else:
                m, c = 0.0000037, 0

        # next define output as per model
        output = m*P*A*G + c

        # output temperature cannot be below room temperature
        if output < 20:
            output = 20

        # we round to 2 decimal places and return
        return round(output, 2)

#--------------------------------------------------------------------------------------------------------------

    # MODEL 3 (private): Linear relationship with sqrt(P*G)*A of the form y = mx + c
    def __model3(self, P, A, G):
        # first define c in y = mx + c
        c = 2.3
        # next define m
        m = 0.0037

        # next define output as per model
        output = m*(math.sqrt(P*G))*A + c

        # output temperature cannot be below room temperature
        if output < 20:
            output = 20

        # we round to 2 decimal places and return
        return round(output, 2)

#--------------------------------------------------------------------------------------------------------------

    # MODEL 4 (private): Linear relationship with sqrt(P*G)*A of the form y = mx + c, but coefficients of the linear
    # relationship (m and c) vary with different values of P and T. - (REALISTIC MODEL)
    def __model4(self, P, A, G):
        # TODO: Set Parameters
        if P < 5000:
            # A < 30
            if A < 30:
                m, c = 0.0015, 0.4
            # 30 <= A < 75
            elif A < 75:
                m, c = 0.00179, 0.31
            # 75 <= A <= 100
            else:
                m, c = 0.0037, 0

        # 5000 <= P < 15000
        elif P < 15000:
            #  A < 35
            if A < 35:
                m, c = 0.0024, 0.39
            # 35 <= A < 77
            elif A < 77:
                m, c = 0.0030, 0.32
            # 77 <= A <= 100
            else:
                m, c = 0.00424, 0

        # 15000 <= P < 35000
        elif P < 35000:
            # A < 40
            if A < 40:
                m, c = 0.0035, 0.35
            # 40 <= A < 80
            elif A < 80:
                m, c = 0.0039, 0.3
            # 80 <= A
            else:
                m, c = 0.0048, 0

        # P >= 35000
        else:
            # A < 300
            if A < 50:
                m, c = 0.00401, 0.3
            # 300 <= A < 700
            elif A < 90:
                m, c = 0.0046, 0.28
            # 700 <= A
            else:
                m, c = 0.00498, 0

        # next define output as per model
        output = m*(math.sqrt(P*G))*A + c

        # output temperature cannot be below room temperature
        if output < 20:
            output = 20

        # we round to 2 decimal places and return
        return round(output, 2)

#--------------------------------------------------------------------------------------------------------------

    # MODEL 5 (private): flow rate = a*P + b*A + c*G
    def __model5(self, P, A, G):
        # define a in a*P + b*A + c*T
        a = 0.005
        # define b
        b = 0.53
        # define c
        c = 0.47

        # next define output as per model
        output = a*P + b*A + c*G

        # output temperature cannot be below room temperature
        if output < 20:
            output = 20

        return round(output, 2)

#--------------------------------------------------------------------------------------------------------------

    # RETRIEVE_OUT_VAL (public): Function used by external programs to obtain values ot output from the
    # environment given parameters P, A and G.
    def retrieve_out_val(self, P, A, G):
        # THE DEFAULT MODEL NUMBER IS 1
        if self.__model_no == 2:
            return self.__model2(P, A, G)

        elif self.__model_no == 3:
            return self.__model3(P, A, G)

        elif self.__model_no == 4:
            return self.__model4(P, A, G)

        elif self.__model_no == 5:
            return self.__model5(P, A, G)

        return self.__model1(P, A, G)

#--------------------------------------------------------------------------------------------------------------
# END OF CLASS #
