import numpy as n
import random as r

def strategy(tile, nearx, neary, types, energies, yourenergy, memory):
    target = -1
    if len(energies) > 0:
        couldbenice = energies < 0.9 * yourenergy
        couldbeeaten = (types != 0) * (types != 1) * (types != 2)
        menu = energies * couldbenice * couldbeeaten
        if not (menu == 0).all():
            target = n.where(menu == n.amax(menu))[0][0]
    dx = 0
    dy = 0
    if target != -1:
        #print(target)
        dx = r.randint(-3,3)
        dy = r.randint(-3,3)
    if len(energies) > 0:
        return n.array([dx, dy]), 0.9 * yourenergy > 2 * n.amax(energies), target, [], [], [[255,255,255]]
    else:
        return n.array([dx, dy]), False, target, [], [], [[255,255,255]]
