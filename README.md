Welcome to the documentation of this game!
This is the code for a competition game, where players create code which controls agents in a simulated environment, with the goal of surviving for a set amount of time.
Before explaining how to use the program, I'll explain the detail behind the game mechanics.

   ***GAME MECHANICS***
   (Skip if you have already seen the introduction video.)

1. The world is finite yet toroidal, by which I mean that there is no "world border". If you go too far to the right, you'll wrap around the world and appear on the other side.
2. The world is a grid. Each grid point can be one of four different "biomes": Desert(ID:1), Grass(ID:2), Jungle(ID:3) and Mountain(ID:4). There's also the occasional Oasis(ID:0). Biomes also have a constant "drain value" (Oasis: 0.4, Desert: 0.6, Grass: 0.5, Jungle: 0.6, Mountain: 0.6) and a "radius value" (Oasis: 3, Desert: 3, Grass: 4, Jungle: 3, Mountain: 2).
3. Players move by submitting a vector coordinate every game tick. It is clipped with the biome radius value of the grid point the player is on, and gets added to their current coordinate.
4. Players have a value called their "energy". Various actions can change this value(Decrease: Moving around(length of vector coordinate, raised to the power of twice the drain value), Chasing(Same as moving, will be explained later), Splitting(halves your energy). Increase: Consumption of foliage and players(If successful, 90% of the "prey"'s energy.)). If the energy becomes equal to or under zero, the player is considered dead and is eliminated from the game.
5. Players can "chase" another object. By selecting a chase target, if the target is close enough, the player is automatically teleported on to the target's position after the target as moved, which allows one to guarantee a collision with the target. This is to prevent pointlessly drawn out chase sequences. If two players simultaneously chase each other, they will simply switch places. The energy deduction calculation is done the same way for chasing and normal movement.
6. Players can also "split". When a player chooses to split, a duplicate player is spawned, and both players' energies are halved. The clone's memory is altered to be the "split memory", which the player assigns when the split took place. Clones are considered allies(denoted by the type being -2, instead of -1 like the other players), and will simply pass through each other instead of fighting when their positions overlap.
7. Players consist of a "strategy file", which contains a function called "strategy". The strategy function takes (in order) the ID of the tile the player is on, the relative x coordinate of nearby objects, the relative y coordinate of the objects, the "type" of the objects(The ID of NPOs(Non-player objects), -1 for players, -2 for allies), the energy values of the objects, the player's energy and the player's memory as input. Then it must output (in order) the movement vector(a numpy array containing 2 integers), whether to split(a single boolean value), the chase target(the index of the object you want to chase, -1 if you don't intend to chase anything), the player's memory, the split copy's memory(Output this even if you don't intend to split.) and a "server ping".(For normal players, you use this to set the player's color. It should look ilke this: [[R,G,B]] It can do more things, but you need special permissions for that, which only the NPOs have.)

   ***INSTRUCTIONS***

Now I will explain how to actually use this program.
The code does have a few comments in it to help you play around with it, but I'll provide more thorough step-by-step instructions here.

   *1. Installation*
You don't need to do anything fancy to get this program on to your computer.
1. Make sure you have Python 3 installed on your computer. Installing Python is a bit outside of the scope for this document, but a few Google searches should get you there.

You also need some Python libraries installed.
Crucial libraries(the program will not run at all without these installed): numpy, random.
Optional libraries(some features use these, but you can disable them and still run it): PIL(the Python Image Library), pygame, time, traceback.

2. Either clone this repository or click the "Download ZIP" button under the "<> Code" tab and extract the ZIP file.
3. To test that everything is working correctly, enter the StrandedInAIsland folder and run simulator.py. The default settings has every feature enabled(rendering, verbose data printing, binary file log export). Hopefully, it shouldn't give you an error, and you should see dots zooming around a pixelized map for a few seconds or minutes, and a "Do you want to export the data? (y/n)" message should appear. Type 'n' for now, and the program should terminate. Next, try executing importer.py. It should start a basic text-based interface. Try typing "help"(It's case sensitive). It should list a series of commands. These are the commands that let you navigate through an exported game recording. Type "play", and it should say "When should the playback stop? destination(0 ~ 999) >". Type 500. You should see more dots zooming about on the screen, only more quickly than before. The program is playing back a pre-recorded game file, more specifically, it's loading the binary file "Logs/BinaryExport.bin". Type 'help' again and try fooling around with the other commands (Don't try "console" for now, to reduce confusion). Hopefully, none of them should give an error.

   *2. Strategy files inside strategy folders*
   
Now I'll go through how to create your own strategy, and navigate your way around some of the settings.
      How to create a strategy
   1. Inside the StrandedInAIsland folder, you will see a folder called Strategies. Inside this folder, there should be(by default) two folders: ExampleStrats and Nature. Examplestrats contains, well, the example strategies. Nature contains the strategy files for NPOs like trees, cacti, bushes, etc. To create your own strategies, create a folder with whatever name you want, and inside it, create a Python file with whatever name you want.
   The mininum setup for this file should be something like:
```py
import numpy
def strategy(tile, nearx, neary, neartype, nearyenrg, myenerg, memory):
    movement = numpy.array([1,0]) #Moves right every tick
    shouldsplit = False #Doesn't split
    chasetarget = -1 #Doesn't chase
    newmemory = [] #Doesn't store anything in memory
    splitmemory = [] #Won't store anything in split copy's memory
    color = [10,10,200] #Color is Blue
    return movement, shouldsplit, chasetarget, newmemory, splitmemory, [color] #Note how the color information is in another set of brackets.
```
  
   2. For testing purposes, try saving your file and run simulator.py. You should see no change. This is because simulator.py is not yet aware that you have created a strategy. To change this, open simulator.py in a text editor or in your IDE. Under "Stuff you'll modify a lot.", You should see a list called "players", inside of which you'll find the two entries "ExampleStrats.Monkey" and "ExampleStrats.Collector". This list is where all the names of the players' strategy files should be.
   3. Add another entry to this list in the format of "*(Whatever your folder name was)*.*(Whatever your file name was(leave out the extension.))*".
   4. Try running simulator.py again. This time, you should see a bunch of blue dots, slowly going right a pixel at a time. If so, congratulations, you have successfully created your first strategy file!

 Some settings

 When you open simulator.py, you should see a flood of comments at the every beginning. Those comments detail what exactly each parameter at the beginning of the file does. Rather than trying to list every setting in this document, the reader is encouraged to explore the file, read the comments and try tweaking things for themselves.
