import numpy as n
import time as t
import pygame as p
from PIL import Image as i

try:
    file = open("Log/BinaryExport.bin", "rb")
    source = list(file.read())
    file.close()
    safe = True
except FileNotFoundError:
    print("It seems that you haven't actually exported a simulation yet. To do that, run simulator.py with logstuff set to True.")
    safe = False
if safe:
    mapimage = n.asarray(i.open("Log/map.png"))
    mapx = len(mapimage)
    mapy = len(mapimage[0])

    initialunpack = []
    index = 0
    clock = t.time()
    while index < len(source):
        size = 65536 * source[index] + 256 * source[index + 1] + source[index + 2]
        if index == 0:
            size *= 12
        else:
            size *= 7
        if t.time() - clock >= 2:
            print("Processed", index, "bytes out of", len(source))
            clock = t.time()
        initialunpack.append(n.array(source[index + 3 : index + 3 + size]))
        index = index + 3 + size
    print("Initial processing done.")

    primarycontroller = None #2 bytes
    primaryxcoord = None #2 bytes
    primaryycoord = None #2 bytes
    indices = [] #3 bytes
    vecx = [] #4 bits
    vecy = [] #4 bits
    energies = [] #2 bytes
    colR = [] #3 bits
    colG = [] #2 bits
    colB = [] #3 bits

    clock = t.time()
    for x in range(len(initialunpack)):
        if t.time() - clock >= 2:
            print("Unpacking timestep", x)
            clock = t.time()
        cut = initialunpack[x]
        if x == 0:
            nums = int(len(cut) / 12)
            primcon = 256 * cut[3 * nums : 4 * nums] + cut[4 * nums : 5 * nums]
            primx = 256 * cut[5 * nums : 6 * nums] + cut[6 * nums : 7 * nums]
            primy = 256 * cut[7 * nums : 8 * nums] + cut[8 * nums : 9 * nums]
            energy = 256 * cut[9 * nums : 10 * nums] + cut[10 * nums : 11 * nums]
            color = cut[11 * nums : 12 * nums]
            primarycontroller = primcon
            primaryxcoord = primx
            primaryycoord = primy
            energies.append(energy)
            colR.append((color / 32).astype(int) * 32)
            colG.append(((color % 32) / 8).astype(int) * 64)
            colB.append((color % 8) * 32)
        else:
            nums = int(len(cut) / 7)
            index = 65536 * cut[:nums] + 256 * cut[nums : 2 * nums] + cut[2 * nums : 3 * nums]
            coord = cut[3 * nums : 4 * nums]
            energy = 256 * cut[4 * nums : 5 * nums] + cut[5 * nums : 6 * nums]
            color = cut[6 * nums : 7 * nums]
            indices.append(index)
            vecx.append((coord / 16).astype(int) - 8)
            vecy.append(coord % 16 - 8)
            energies.append(energy)
            colR.append((color / 32).astype(int) * 32)
            colG.append(((color % 32) / 8).astype(int) * 64)
            colB.append((color % 8) * 32)
    del x
    print("Data unpacking done.")

    def renderscreen(colormap, xcoord, ycoord, colors):
        screen = colormap.copy()
        screen[xcoord, ycoord, 0] = colors[0]
        screen[xcoord, ycoord, 1] = colors[1]
        screen[xcoord, ycoord, 2] = colors[2]
        return screen

    p.init()
    display = p.display.set_mode((mapx, mapy), flags=p.SCALED)
    p.display.set_caption("islands lol")
    running = True
    howlong = len(initialunpack)
    fps = 1000
    print("___________________________\nHello there! Welcome to the game binary importer!")
    print("You can type a few commands to view the imported simulation.")
    print("Use 'help' to view the possible commands and 'play' to play back the simulation.")
    while True:
        command = input("simulator >")
        if command == 'help':
            print("The available commands are:\n")
            print("play   -Starts the playback.\n")
            print("resume   -Resumes a previously terminated playback.\n")
            print("fps   -Sets the FPS for the playback(no frames are skipped.)\n")
            print("advance  -Advances the playback by a few timesteps.")
            print("show   -Shows the current frame.")
            print("console  -Lets you type Python code directly.")
        if command == 'play':
            destination = int(input("When should the playback stop?\ndestination(0 ~ " + str(howlong - 1) + ") >"))
            print("You can interrupt the simulation at any time.")
            x = 0
            oldx = primaryxcoord
            oldy = primaryycoord
            try:
                display = p.display.set_mode((mapx, mapy), flags=p.SCALED)
                clock = t.time()
                while x < min(howlong, destination) and running:
                    if x != howlong - 1:
                        screen = renderscreen(mapimage, oldx, oldy, [colR[x], colG[x], colB[x]])
                        surf = p.surfarray.make_surface(screen)
                        for event in p.event.get():
                            if event.type == p.QUIT:
                                running = False
                        display.blit(surf, (0, 0))
                        p.display.update()
                        mappx = oldx[indices[x]]
                        mappy = oldy[indices[x]]
                        oldx = (mappx + vecx[x]) % mapx
                        oldy = (mappy + vecy[x]) % mapy
                        while (t.time() - clock) * fps < 1:
                            x = x
                        clock = t.time()
                    x += 1
            except KeyboardInterrupt:
                print("KeayboardInterrupt")
            p.display.set_mode((mapx, mapy), flags=p.HIDDEN)
            print("Simulation terminated on timestep " + str(x))
        if command == 'resume':
            if not 'x' in globals():
                print("You can't resume before you start the playback. Use the command 'play'.")
            else:
                if x >= howlong:
                    print("The simulation playback seems to have already completed.")
                else:
                    print("Resuming playback from timestep " + str(x))
                    try:
                        display = p.display.set_mode((mapx, mapy), flags=p.SCALED)
                        clock = t.time()
                        while x < howlong and running:
                            if x != howlong - 1:
                                screen = renderscreen(mapimage, oldx, oldy, [colR[x], colG[x], colB[x]])
                                surf = p.surfarray.make_surface(screen)
                                for event in p.event.get():
                                    if event.type == p.QUIT:
                                        running = False
                                display.blit(surf, (0, 0))
                                p.display.update()
                                mappx = oldx[indices[x]]
                                mappy = oldy[indices[x]]
                                oldx = (mappx + vecx[x]) % mapx
                                oldy = (mappy + vecy[x]) % mapy
                                while (t.time() - clock) * fps < 1:
                                    x = x
                                clock = t.time()
                            x += 1
                    except KeyboardInterrupt:
                        print("KeayboardInterrupt")
                    p.display.set_mode((mapx, mapy), flags=p.HIDDEN)
                    print("Simulation terminated on timestep " + str(x))
        if command == 'fps':
            fps = float(input("What maximum FPS do you want?\nfps >"))
            print("FPS set to " + str(fps))
        if command == 'advance':
            if not 'x' in globals():
                print("You can't advance before you start the playback. Use the command 'play'.")
            else:
                if x >= howlong:
                    print("The simulation playback seems to have already completed.")
                else:
                    stepcount = min(max(0, int(input("Advance by how many timesteps?\nadvance >"))), howlong - x - 1)
                    for step in range(stepcount):
                        mappx = oldx[indices[x]]
                        mappy = oldy[indices[x]]
                        oldx = (mappx + vecx[x]) % mapx
                        oldy = (mappy + vecy[x]) % mapy
                        x += 1
                    print("Advanced to timestep " + str(x))
        if command == 'show':
            if not 'x' in globals():
                print("The frame cannot be shown before you start the playback. Use the command 'play'.")
            else:
                screen = renderscreen(mapimage, oldx, oldy, [colR[x], colG[x], colB[x]])
                (i.fromarray(n.swapaxes(screen, 0, 1))).show()
        if command == 'console':
            if not 'traceback' in globals():
                if input("This requires the traceback library, is that okay?\nreply(y/n) >") == 'y':
                    import traceback
            print("Type quit() to quit the console and return to the importer.")
            while True:
                prompt = input("console >")
                if prompt == "quit()":
                    break
                else:
                    try:
                        exec("rommand = '" + prompt + "'")
                        exec(rommand)
                    except:
                        print(traceback.format_exc())

