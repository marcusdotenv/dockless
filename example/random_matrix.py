import numpy as np

def handle(**args):
    matrix = np.random.rand(args["lines"], args["cols"]) 
    return { "matrix": matrix.tolist() }