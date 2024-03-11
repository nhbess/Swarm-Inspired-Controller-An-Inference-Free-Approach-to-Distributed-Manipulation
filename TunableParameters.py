class TunableParameters:
    shrink_x = 0.5       # Optimal Value
    threshold_x_a = 0.16 # Optimal Value

    excitation_factor = 1  # fixed for now

    @staticmethod
    def printValues():
        print("Parameters:",TunableParameters.shrink_x,TunableParameters.threshold_x_a)#,TunableParameters.shrink_x_b,TunableParameters.threshold_x_b)

