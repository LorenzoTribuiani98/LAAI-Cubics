import numpy as np

def function(flag, func):
    if flag:
        func()

def hello():
    print("Fuck yea motherfuckers")

function(False, hello)