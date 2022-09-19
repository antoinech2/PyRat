# %%
"""
<h1><b><center>How to use this file with PyRat?</center></b></h1>
"""

# %%
"""
Google Colab provides an efficient environment for writing codes collaboratively with your group. For us, teachers, it allows to come and see your advancement from time to time, and help you solve some bugs if needed.

The PyRat software is a complex environment that takes as an input an AI file (as this file). It requires some resources as well as a few Python libraries, so we have installed it on a virtual machine for you.

PyRat is a local program, and Google Colab is a distant tool. Therefore, we need to indicate the PyRat software where to get your code! In order to submit your program to PyRat, you should follow the following steps:

1.   In this notebook, click on *Share* (top right corner of the navigator). Then, change sharing method to *Anyone with the link*, and copy the sharing link;
2.   On the machine where the PyRat software is installed, start a terminal and navigate to your PyRat directory;
3.   Run the command `python ./pyrat.py --rat "<link>" <options>`, where `<link>` is the share link copied in step 1. (put it between quotes), and `<options>` are other PyRat options you may need.
"""

# %%
"""
<h1><b><center>Pre-defined constants</center></b></h1>
"""

# %%
"""
A PyRat program should -- at each turn -- decide in which direction to move. This is done in the `turn` function later in this document, which should return one of the following constants:
"""

# %%
MOVE_DOWN = 'D'
MOVE_LEFT = 'L'
MOVE_RIGHT = 'R'
MOVE_UP = 'U'

# %%
"""
<h1><b><center>Your coding area</center></b></h1>
"""

# %%
"""
Please put your functions, imports, constants, etc. between this text and the PyRat functions below. You can add as many code cells as you want, we just ask that you keep things organized (one function per cell, commented, etc.), so that it is easier for the teachers to help you debug your code!
"""

# %%
import random
visited_locations = []

# %%
def random_move () :
    all_moves = [MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP]
    return random.choice(all_moves)

# %%
def move_from_locations (source_location, target_location) : 
    difference = (target_location[0] - source_location[0], target_location[1] - source_location[1])
    if difference == (0, -1) :
        return MOVE_DOWN
    elif difference == (0, 1) :
        return MOVE_UP
    elif difference == (1, 0) :
        return MOVE_RIGHT
    elif difference == (-1, 0) :
        return MOVE_LEFT
    else :
        raise Exception("Impossible move")

# %%


# %%


# %%


# %%
"""
<h1><b><center>PyRat functions</center></b></h1>
"""

# %%
"""
The `preprocessing` function is called at the very start of a game. It is attributed a longer time compared to `turn`, which allows you to perform intensive computations. If you store the results of these computations into **global** variables, you will be able to reuse them in the `turn` function.

*Input:*
*   `maze_map` -- **dict(pair(int, int), dict(pair(int, int), int))** -- The map of the maze where the game takes place. This structure associates each cell with the dictionry of its neighbors. In that dictionary of neighbors, keys are cell coordinates, and associated values the number of moves required to reach that neighbor. As an example, `list(maze_map[(0, 0)].keys())` returns the list of accessible cells from `(0, 0)`. Then, if for example `(0, 1)` belongs to that list, one can access the number of moves to go from `(0, 0)` to `(0, 1)` by the code `maze_map[(0, 0)][(0, 1)]`.
*   `maze_width` -- **int** -- The width of the maze, in number of cells.
*   `maze_height` -- **int** -- The height of the maze, in number of cells.
*   `player_location` -- **pair(int, int)** -- The initial location of your character in the maze.
*   `opponent_location` -- **pair(int,int)** -- The initial location of your opponent's character in the maze.
*   `pieces_of_cheese` -- **list(pair(int, int))** -- The initial location of all pieces of cheese in the maze.
*   `time_allowed` -- **float** -- The time you can take for preprocessing before the game starts checking for moves.

*Output:*
*   This function does not output anything.
"""

# %%
def preprocessing (maze_map, maze_width, maze_height, player_location, opponent_location, pieces_of_cheese, time_allowed) :
    pass

# %%
"""
The `turn` function is called each time the game is waiting
for the player to make a decision (*i.e.*, to return a move among those defined above).

*Input:*
*   `maze_map` -- **dict(pair(int, int), dict(pair(int, int), int))** -- The map of the maze. It is the same as in the `preprocessing` function, just given here again for convenience.
*   `maze_width` -- **int** -- The width of the maze, in number of cells.
*   `maze_height` -- **int** -- The height of the maze, in number of cells.
*   `player_location` -- **pair(int, int)** -- The current location of your character in the maze.
*   `opponent_location` -- **pair(int,int)** -- The current location of your opponent's character in the maze.
*   `player_score` -- **float** -- Your current score.
*   `opponent_score` -- **float** -- The opponent's current score.
*   `pieces_of_cheese` -- **list(pair(int, int))** -- The location of remaining pieces of cheese in the maze.
*   `time_allowed` -- **float** -- The time you can take to return a move to apply before another time starts automatically.

*Output:*
*   A chosen move among `MOVE_UP`, `MOVE_DOWN`, `MOVE_LEFT` or `MOVE_RIGHT`.
"""

# %%
def turn (maze_map, maze_width, maze_height, player_location, opponent_location, player_score, opponent_score, pieces_of_cheese, time_allowed) :
    # Declare visited_locations as an existing global variable
    global visited_locations
    # Add the current location inside it if not already there
    if player_location not in visited_locations :
        visited_locations.append(player_location)
    
    all_direction = list(maze_map[player_location].keys())
    non_explored_directions = []
    for direction in all_direction:
      if direction not in visited_locations:
        non_explored_directions.append(direction)
    
    if len(non_explored_directions) == 0 :
      return move_from_locations(player_location, random.choice(all_direction))
    else:
      return move_from_locations(player_location, random.choice(non_explored_directions))