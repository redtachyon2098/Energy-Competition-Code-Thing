import random as r
import numpy as n

def strategy(tile, nearx, neary, types, energies, yourenergy, memory):
    return n.array([r.randint(-4,4), r.randint(-4,4)]), r.randint(0,100) == 0, r.randint(-1, 0), [], [], [[10,10,10]]
