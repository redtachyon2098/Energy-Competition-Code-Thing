import numpy as n
import random as r
import gc
#_______________Every value and function worth modifying__________
verbose = True
render = True
stuff = True
howmanytimesteps = 1000
viewradius = 5
biomesize = 30
mapx = 200
mapy = 200
NPCs = [
    "Nature.Tree",
    "Nature.Sequoia",
    "Nature.Apple",
    "Nature.Bush",
    "Nature.Fern",
    "Nature.Cactus"]
NPCAmounts = [200, 200, 0, 100, 100, 100]
NPCEnergy = [10, 10, 100, 100, 100, 100]
NPCpermissions = [True, True, False, True, True, True]
NPCConsumable = [False, False, True, True, True, True]
NPCHostility = [False, False, False, False, False, False]
players = [
    "ExampleStrats.Monkey",
    "ExampleStrats.Collector"]
playerAmount = 1000
playerEnergy = 1000
howmanybiomes = 5 #oasis, desert, grass, jungle, mountain
drainvalues = n.array([0.4, 0.6, 0.5, 0.6, 0.6])
radiusvalues = n.array([3, 2, 3, 3, 2])
biomecolors = n.array([[5,220, 100],[160,140,20],[40,220,5],[10,200,30],[10,80,10]])

def SpawnCondition(tile, name):
    if name == "Nature.Tree":
        return tile != 1
    elif name == "Nature.Sequoia":
        return tile == 3
    elif name == "Nature.Bush":
        return tile != 1
    elif name == "Nature.Fern":
        return tile == 3
    elif name == "Nature.Cactus":
        return tile == 1
    else:
        return True

def DrainEnergy(en, k, dist):
    return en - dist ** k - 0.1

def combat(yourE, enemyE):
    if yourE > enemyE:
        return yourE + enemyE * 0.9
    else:
        return 0
#______________All the other stuff.______________
if render:
    import pygame as p
if verbose:
    import time as t
if logstuff:
    from PIL import Image as i
nams = NPCs + players
strs = []
typs = n.array(list(range(len(NPCs))) + [-1] * len(players))   #positive numbers for foliage, -1 for all else.
amounts = NPCAmounts + [playerAmount] * len(players)         #How many abominations shall we spawn?
perms = NPCpermissions + [False] * len(players) #Special admin permissions!
energ = NPCEnergy + [playerEnergy] * len(players)       #Starting energy?
consu = n.array(NPCConsumable + [True] * len(players))  #Consumable?
hosti = n.array(NPCHostility + [True] * len(players)) #Hostile?
# Input: tile, nearx, neary, types, energy, yourenergy, memory
#Output: direction, split, chase, memory, splitmemory, ping

#Import the Strat Files.
if verbose:
    print("Import the Strat Files")
for x in nams:
    exec("import Strategies." + x + " as g")
    strs.append(g.strategy)
if verbose:
    print("Imported the Strat Files")

#Make Map
if verbose:
    print("Make Map")
initi = n.random.rand(mapx, mapy)
convx = int(biomesize)
convy = int(biomesize)
conv = n.random.rand(convx, convy)
ring = n.roll(n.roll(conv, 1, axis=0), 1, axis=1) + n.roll(n.roll(conv, 1, axis=0), 0, axis=1) + n.roll(n.roll(conv, 1, axis=0), -1, axis=1) + n.roll(conv, 1, axis=1) + n.roll(conv, -1, axis=1) + n.roll(n.roll(conv, -1, axis=0), 1, axis=1) + n.roll(n.roll(conv, -1, axis=0), 0, axis=1) + n.roll(n.roll(conv, -1, axis=0), -1, axis=1)
conv += ring
world = n.zeros_like(initi)
for x in range(convx):
    xax = n.roll(initi, x, axis=0)
    for y in range(convy):
        world += n.roll(xax, y, axis=1) * conv[x,y]
world -= n.amin(world)
biome = (world * (howmanybiomes - 0.01) / n.amax(world)).astype(int)
drain = drainvalues[biome]
radii = radiusvalues[biome]
colormap = biomecolors[biome]
if verbose:
    print("Made Map")

if logstuff:
    im = i.fromarray((n.swapaxes(colormap, 0, 1)).astype("uint8"))
    im.save("Log/Map.png")

#Prep Characters.
if verbose:
    print("Prep Characters")

xcoord = []
ycoord = []
controller = []
energy = []
memories = []
for x in range(len(amounts)):
    for y in range(amounts[x]):
        for attempt in range(100):
            xc = r.randint(0, mapx - 1)
            yc = r.randint(0, mapy - 1)
            if SpawnCondition(biome[xc, yc], nams[x]):
                xcoord.append(xc)
                ycoord.append(yc)
                controller.append(x)
                energy.append(energ[x])
                memories.append([])
                break
xcoord = n.array(xcoord)
ycoord = n.array(ycoord)
controller = n.array(controller)
energy = n.array(energy)
memories = n.array(memories, dtype=object)
typ = typs[controller]
indices = n.arange(len(controller))
if verbose:
    print("Prepped Characters")

#Main Loop?
if verbose:
    print("Main Loop?")

def getinput(index, strat, xcor, ycor, energ, memory):
    view = biome[xcor, ycor]
    nearbx = n.abs(xcoord - xcor) <= viewradius
    nearby = n.abs(ycoord - ycor) <= viewradius
    nearby = nearbx * nearby != 0
    nearby[index] = False
    nx = xcoord[nearby] - xcor
    ny = ycoord[nearby] - ycor
    ne = energy[nearby]
    nt = typ[nearby]
    nt[controller[nearby] == controller[index]] = -2
    ni = indices[nearby]
    direction, split, chasetarget, memory, splitmemory, ping = strat(view, nx, ny, nt, ne, energ, memory)
    radius = radii[xcor, ycor]
    direction = n.clip(direction, -radius, radius)
    if chasetarget != -1 and chasetarget < len(ni):
        chasetarget = ni[chasetarget]
    return direction[0], direction[1], split, chasetarget, memory, splitmemory, ping

if render:
    p.init()
    display = p.display.set_mode((mapx, mapy), flags=p.SCALED)
    p.display.set_caption("islands lol")
running = True
for timestep in range(howmanytimesteps):
    if verbose:
        clock = t.time()
    mx = []
    my = []
    me = []
    mm = []
    mc = []
    mcol = []
    chasers = []
    chasees = []
    cx = []
    cy = []
    ce = []
    cm = []
    cc = []
    ccol = []
    for x in range(len(controller)): #General Movement
        nx, ny, split, chasetarget, memory, splitmemory, ping = getinput(x, strs[controller[x]], xcoord[x], ycoord[x], energy[x], memories[x])
        mx.append((xcoord[x] + nx) % mapx)
        my.append((ycoord[x] + ny) % mapy)
        if consu[controller[x]]:
            me.append(DrainEnergy(energy[x], drain[xcoord[x], ycoord[x]], (nx ** 2 + ny ** 2)))
        else:
            me.append(energy[x])
        mm.append(memory)
        mc.append(controller[x])
        mcol.append(ping[0])
        if chasetarget != -1:
            chasers.append(x)
            chasees.append(chasetarget)
        if split: #Splitting
            cx.append(mx[x])
            cy.append(my[x])
            me[x] /= 2
            ce.append(me[x])
            cm.append(splitmemory)
            cc.append(mc[x])
            ccol.append(mcol[x])
        if perms[controller[x]] and len(ping) == 2: #Special permission to execute code
            instruction = ping[-1]
            exec(instruction, globals(), locals())
    for x in range(len(chasers)): #Chasing
        guy = chasers[x]
        tar = chasees[x]
        radius = radii[mx[guy], my[guy]]
        dx = mx[tar] - mx[guy]
        dy = my[tar] - my[guy]
        if dx > 0:
            if dx > mapx / 2:
                dx = dx - mapx
        if dx < 0:
            if -dx > mapx / 2:
                dx = dx + mapx
        if dy > 0:
            if dy > mapy / 2:
                dy = dy - mapy
        if dy < 0:
            if -dy > mapy / 2:
                dy = dy + mapy
        dx = min(max(dx, -radius), radius)
        dy = min(max(dy, -radius), radius)
        mx[guy] = (mx[guy] + dx) % mapx
        my[guy] = (my[guy] + dy) % mapy
        me[guy] = DrainEnergy(me[guy], drain[mx[guy], my[guy]], (dx ** 2 + dy ** 2))
    #Combine the OGs with the split clones
    mx += cx
    my += cy
    me += ce
    mm += cm
    mc += cc
    mcol += ccol
    #Prune all dead players, turn list into numpy array.
    alive = n.array(me) > 0
    xco = n.array(mx)[alive]
    yco = n.array(my)[alive]
    eng = n.array(me)[alive]
    con = n.array(mc)[alive]
    mem = n.array(mm, dtype=object)[alive]
    col = n.array(mcol)[alive]
    hostile = hosti[con]
    consumable = consu[con]
    #Collision detection.
    calcdE = []
    for x in range(len(xco)):
        onx = xco == xco[x]
        ony = yco == yco[x]
        foreign = con != con[x]
        enemies = onx * ony * foreign * consumable
        if enemies.any() and hostile[x]:
            frontier = n.amax(eng[enemies])
            newE = combat(eng[x], frontier)
            calcdE.append(newE)
        elif enemies.any() and consumable[x]:
            frontier = n.amax(eng[enemies])
            if frontier < eng[x]:
                calcdE.append(eng[x])
            else:
                calcdE.append(0)
        else:
            calcdE.append(eng[x])
    calcdE = n.array(calcdE)
    nextgen = calcdE > 0
    xcoord = xco[nextgen]
    ycoord = yco[nextgen]
    controller = con[nextgen]
    energy = calcdE[nextgen]
    memories = mem[nextgen]
    colors = col[nextgen]
    typ = typs[controller]
    indices = n.arange(len(controller))
    if render:
        screen = colormap.copy()
        screen[xcoord, ycoord] = colors
        surf = p.surfarray.make_surface(screen)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
        display.blit(surf, (0, 0))
        p.display.update()
        gc.collect()
    if verbose:
        print(1 / (t.time() - clock), "FPS at", len(controller) / (t.time() - clock), "PPS")
    if logstuff:
        print("")
if render:
    p.quit()
