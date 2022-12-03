import numpy as n
import random as r

def strategy(tile, nearx, neary, types, energies, yourenergy, memory):
    if r.random() < 0.02:
        return n.array([0,0]), False, -1, [], [], [[40, 100, 100], "sx = (mx[x] + r.randint(-4,4)) % mapx\nsy = (my[x] + r.randint(-4,4)) % mapx\nif SpawnCondition(biome[sx, sy], 'Nature.Bush'):\n\tcx.append(sx)\n\tcy.append(sy)\n\tce.append(energ[4])\n\tcm.append([])\n\tcc.append(4)\n\tccol.append([40, 100, 100])"]
    else:
        return n.array([0,0]), False, -1, [], [], [[40, 100, 100], ""]
