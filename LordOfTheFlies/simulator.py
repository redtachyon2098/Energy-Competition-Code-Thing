import numpy as n
import random as r
#_______________Stuff you'll modify a lot.__________
verbose = True #This will show some information in the terminal.
render = True #This requires pygame to enable, it will render the map and the players using one piexel per grid/player.
logstuff = True #This makes the code export some game data to a file in the Log folder. It's not complete yet, and it will hog your RAM if you enable it.
players = [ #The names of the actual players must be listed here in order for them to appear in the game. Add your folder to the Strategies folder and put their names here.
    "ExampleStrats.Monkey",
    "ExampleStrats.Collector"]
howmanytimesteps = 1000 #How long do you want the game to run before it auto-terminates?
viewradius = 5 #How far should the players be able to see?
biomesize = 30 #How big should the biomes in the terrain generation be?
biomedetail = 1 #How jagged should the edges of the terrain be?
mapx = 200 #How wide should the map be?
mapy = 200 #How tall should the map be?
NPCs = [ #All the foliage/other stuff that exist in the game. The raw code of each can be found in the Strategies/Nature folder. You can comment out specific objects to stop them from spawning. NOTE: Commenting out "Nature.Apple" without commenting out "Nature.Tree" or "Nature.Sequoia" will break a few things.
    "Nature.Tree",
    "Nature.Sequoia",
    "Nature.Apple",
    "Nature.Bush",
    "Nature.Fern",
    "Nature.Cactus"]
NPCAmounts = [20, 20, 0, 100, 100, 100] #How much should each non-player object initially spawn?
NPCEnergy = [10, 10, 100, 100, 100, 100] #How much energy should each non-player onject initially have?
playerAmount = 100 #How many instances of each strategy should initially spawn?
playerEnergy = 1000 #How much energy should each player initially have?

#_____________Stuff you won't modify much._________________

NPCpermissions = [True, True, False, True, True, True] #Which objects have admin permissions?(Currently used for spawning other objects, but can be used for literally anything.)
NPCConsumable = [False, False, True, True, True, True] #Which objects are consumable? (You can't eat trees, for example.)
NPCHostility = [False, False, False, False, False, False] #Which objects can attack players?
howmanybiomes = 5 #oasis, desert, grass, jungle, mountain
drainvalues = n.array([0.4, 0.6, 0.5, 0.6, 0.6]) #How much does moving around drain your energy? (Depending on the biome ID)
radiusvalues = n.array([3, 3, 4, 3, 2]) #How far can you move every time step? (Depending on the biome ID)
biomecolors = n.array([[5,220, 100],[160,140,20],[40,220,5],[10,200,30],[10,80,10]]) #What color should each biome be?

def SpawnCondition(tile, name): #Where can NPOs spawn?
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

def DrainEnergy(en, k, dist): #How much energy is drained when moving?
    return en - dist ** k - 0.1

def combat(yourE, enemyE): #How much energy do you gain when you attack something?
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
mconvx = n.outer(n.arange(int(convx / biomedetail)) - int(convx / (2 * biomedetail)), n.zeros((int(convy / biomedetail))) + 1)
mconvy = n.outer(n.zeros((int(convx / biomedetail))) + 1, n.arange(int(convy / biomedetail)) - int(convy / (2 * biomedetail)))
metaconv = 1 / ((mconvx / (convx / biomedetail)) ** 2 + (mconvy / (convy / biomedetail)) ** 2 + 1)
applied = n.zeros_like(conv)
for x in range(int(convx / biomedetail)):
    xax = n.roll(conv, x, axis=0)
    for y in range(int(convy / biomedetail)):
        applied += n.roll(xax, y, axis=1) * metaconv[x,y]
conv = applied
conv -= n.amin(conv)
conv /= n.amax(conv) / 4
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
    #print(index, chasetarget, len(ni))
    if chasetarget != -1 and chasetarget < len(ni):
        chasetarget = ni[chasetarget]
    else:
        chasetarget = -1
    return direction[0], direction[1], split, chasetarget, memory, splitmemory, ping

if render:
    p.init()
    display = p.display.set_mode((mapx, mapy), flags=p.SCALED)
    p.display.set_caption("islands lol")
if logstuff:
    finalbinary = bytes()
running = True
try:
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
        ci = []
        for x in range(len(controller)): #General Movement
            nx, ny, split, chasetarget, memory, splitmemory, ping = getinput(x, strs[controller[x]], xcoord[x], ycoord[x], energy[x], memories[x])
            mx.append(nx)
            my.append(ny)
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
                ci.append(x)
            if perms[controller[x]] and len(ping) == 2: #Special permission to execute code
                instruction = ping[-1]
                exec(instruction, globals(), locals())
        for x in range(len(chasers)): #Chasing
            guy = chasers[x]
            tar = chasees[x]
            dx = xcoord[tar] + mx[tar] - xcoord[guy] - mx[guy]
            dy = ycoord[tar] + my[tar] - ycoord[guy] - my[guy]
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
            mx[guy] = dx
            my[guy] = dy
            #me[guy] = DrainEnergy(me[guy], drain[mx[guy], my[guy]], (dx ** 2 + dy ** 2))
        #Combine the OGs with the split clones
        oldinds = n.array(list(indices) + ci, dtype=int)
        px = n.array(mx + cx)
        py = n.array(my + cy)
        me = n.array(me + ce)
        mm = n.array(mm + cm, dtype=object)
        mc = n.array(mc + cc)
        mcol = n.array(mcol + ccol)
        prex = xcoord[oldinds]
        prey = ycoord[oldinds]
        px = n.clip(px, -radii[prex, prey], radii[prex, prey])
        py = n.clip(py, -radii[prex, prey], radii[prex, prey])
        mx = (prex + px) % mapx
        my = (prey + py) % mapy
        filtering = consu[mc]
        me[filtering] = DrainEnergy(me, drain[mx, my], py ** 2 + py ** 2)[filtering]
        #Prune all dead players, turn list into numpy array.
        alive = n.array(me) > 0
        xco = mx[alive]
        yco = my[alive]
        eng = me[alive]
        con = mc[alive]
        mem = mm[alive]
        col = mcol[alive] % 256
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
        if len(indices) == 0:
            break
        if logstuff:#primary 3+2+2+2+2+1 secondary 3+1+2+1
            oldinds = oldinds[alive][nextgen]
            indnums = list((oldinds  / 65536).astype(int)) +  list(((oldinds % 65536) / 256).astype(int)) +  list((oldinds % 256).astype(int))
            hexn = indnums.copy()
            if timestep == 0:
                conhex = list(((controller % 65536) / 256).astype(int)) + list(controller % 256)
                xcoordhex = list(((xcoord % 65536) / 256).astype(int)) + list(xcoord % 256)
                ycoordhex = list(((ycoord % 65536) / 256).astype(int)) + list(ycoord % 256)
                hexn += conhex + xcoordhex + ycoordhex
            else:
                px = px[alive][nextgen] + 8
                py = py[alive][nextgen] + 8
                hexn += list(px * 16 + py)
            energyhex = list(((n.clip(energy, 0, 65535) % 65536) / 256).astype(int)) + list(n.clip(energy, 0, 65535).astype(int) % 256)
            hexn += energyhex
            hexn += list(16 * (colors[:,0] / 64).astype(int) + 4 * (colors[:,1] / 64).astype(int) + (colors[:,0] / 64).astype(int))
            hexn = [int(len(controller) / 65536), int((len(controller) % 65536) / 256), len(controller) % 256] + hexn
            finalbinary += bytes(hexn)
        if render:
            screen = colormap.copy()
            screen[xcoord, ycoord] = colors
            surf = p.surfarray.make_surface(screen)
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
            display.blit(surf, (0, 0))
            p.display.update()
        if verbose:
            if logstuff:
                print("Total Binary Size:", len(finalbinary))
            print(1 / (t.time() - clock), "FPS at", len(controller) / (t.time() - clock), "PPS for", len(controller), "players.\n")
    if render:
        p.quit()
except KeyboardInterrupt:
    print("Terminated.")
if logstuff:
    if input("Do you want to export the data? (y/n)") == 'y':
        im = i.fromarray((n.swapaxes(colormap, 0, 1)).astype("uint8"))
        im.save("Log/Map.png")
        file = open("Log/BinaryExport.bin","wb")
        file.write(finalbinary)
        file.close()
        print("Exported log.")
