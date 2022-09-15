#!/usr/bin/python
#    Copyright © 2017 Vincent Gripon (vincent.gripon@imt-atlatique.fr) and IMT Atlantique
#
#    This file is part of PyRat.
#
#    PyRat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyRat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyRat.  If not, see <http://www.gnu.org/licenses/>.

# Imports
from resources.imports.parameters import *
from resources.imports.maze import *
from resources.imports.display import *
import importlib.util
import sys
import time
from queue import Queue
import queue
from threading import Thread
import multiprocessing as mp
import os
import signal
import pygame
import traceback
import datetime
import gdown
import ipynb_py_convert
import json

if args.import_keras:
    import keras

# Sound effects. There are three sounds corresponding to any combination of players taking pieces of cheese at a given moment
try:
    if not(args.nodrawing) and not(args.save_images):
        pygame.mixer.init(frequency = 44100, size = -16, channels = 1, buffer = 2**12)
        effect_left = pygame.mixer.Sound("resources" + os.path.sep + "sounds" + os.path.sep + "cheese_left.wav")
        effect_right = pygame.mixer.Sound("resources" + os.path.sep + "sounds" + os.path.sep + "cheese_right.wav")
        effect_both = pygame.mixer.Sound("resources" + os.path.sep + "sounds" + os.path.sep + "cheese_both.wav")
        nosound = False
    else:
        raise Exception("Error loading sounds")
except:
    effect_left = ""
    effect_right = ""
    effect_both = ""
    nosound = True

# Function to play a sound
def play_sound(effect):
    if nosound or args.nodrawing:
        ()
    else:
        try:
            effect.play()
        except:
            ()

# Function to handle a player, this is intended to be launched by a separate process
def player(pet, filename, q_in, q_out, q_quit, width, height, preparation_time, turn_time):
    # If user provides a Google Colab shared link, we use it
    if filename[:4] == "http" and "colab" in filename :
        file_id = filename.split("/")[-1].split("?")[0]
        url = "https://drive.google.com/uc?id=" + file_id
        base_dir = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "AIs" + os.path.sep
        ipynb_file_name = base_dir + file_id + ".ipynb"
        gdown.download(url, ipynb_file_name)
        with open(ipynb_file_name, "r") as ipynb_file :
            notebook_json = json.load(ipynb_file)
            try :
                notebook_name = notebook_json["metadata"]["colab"]["name"]
            except :
                try :
                    print("Warning: cannot find Colab program name, missing metadata in API")
                    notebook_name = "colab"
                except Exception as e :
                    raise Exception("Error getting colab name, please contact support:", e)
            if notebook_name.endswith(".ipynb"):
                notebook_name = notebook_name[:-len(".ipynb")]
        py_file_name = base_dir + notebook_name + ".py"
        ipynb_py_convert.convert(ipynb_file_name, py_file_name)
        os.remove(ipynb_file_name)
        filename = py_file_name
    # If user provides a local notebook file
    if filename[-6:] == ".ipynb" :
        base_dir = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "AIs" + os.path.sep
        file_id = filename.split(os.path.sep)[-1].split(".ipynb")[0]
        py_file_name = base_dir + file_id + ".py"
        ipynb_py_convert.convert(filename, py_file_name)
        filename = py_file_name
    # We try to launch a regular AI
    try:
        player = importlib.util.spec_from_file_location("player",filename)
        module = importlib.util.module_from_spec(player)
        player.loader.exec_module(module)
        existence = True
    # In case there is a problem, we launch the dummy AI which basically does nothing
    except:
        if filename != "":
            var = traceback.format_exc()
            print("Error: " + var, file=sys.stderr)
            print("Error while loading player controlling " + pet + ", dummy player loaded instead", file=sys.stderr)
        player = importlib.util.spec_from_file_location("player","resources" + os.path.sep + "imports" + os.path.sep + "dummy_player.py")
        module = importlib.util.module_from_spec(player)
        player.loader.exec_module(module)        
        existence = False
    # We retrieve the essential parts
    name = filename.split(str(os.path.sep))[-1].split(".")[0]
    preprocessing = module.preprocessing
    turn = module.turn
    # We communicate our name to the main program
    q_out.put(name)
    # And we get useful information in return
    maze, player1_location, player2_location, pieces_of_cheese = q_in.get()
    # Then we call the preprocessing function and catch any exception
    try:
        before = time.time()
        preprocessing(maze, width, height, player1_location, player2_location, pieces_of_cheese, preparation_time)
        after = time.time()
        prep_time = after - before
        q_out.put("preprocessing")
    except Exception as e:
        traceback.print_exc()
        print(e, file=sys.stderr,)
    # We run each turn through this loop
    try:
        turn_delay = 0
        turn_delay_count = 0
        while 1:
            # We get the new info
            try:
                player1_location, player2_location, score1, score2, pieces_of_cheese = q_in.get()
                while not(q_in.empty()):
                    player1_location, player2_location, score1, score2, pieces_of_cheese = q_in.get()                                        
            except:
                break
            if player1_location == None:
                break
            # Then we check if the main program ask us to exit
            try:
                if q_quit.get():
                    break
            except:
                break
            # We now ask the AI what to do
            if pieces_of_cheese == []:
                break
            try:
                before = time.time()
                decision = turn(maze, width, height, player1_location, player2_location, score1, score2, pieces_of_cheese, turn_time)
                after = time.time()
                turn_delay = turn_delay + (after - before)
                turn_delay_count = turn_delay_count + 1
            except Exception as e:
                traceback.print_exc()
                print(e, file=sys.stderr)
                decision = ""
            # Finally we send the decision to the main program
            try:                
                q_out.put(decision)
            except:
                ()
    except:
        ()
    player1_location, player2_location, score1, score2, pieces_of_cheese = q_in.get()
    if args.postprocessing:
        try:
            module.postprocessing(maze, width, height, player1_location, player2_location, score1, score2, pieces_of_cheese, turn_time)
        except Exception as e:
            traceback.print_exc()        
            print(e, file=sys.stderr,)
    try :
        q_out.put((prep_time, turn_delay / turn_delay_count))
    except :
        q_out.put((0, 0))
    
# Utility function to convert strange time object to float
def convert_time_to_int(datetime):
    return datetime.hour * 3600000 + datetime.minute * 60000 + datetime.second * 1000 + datetime.microsecond / 1000.0

# Convert the decision taken by an AI into an actual new location
def cell_of_decision(location, decision):
    try:
        a, b = location
        if decision == "U":
            return (a,b+1)
        elif decision == "D":
            return (a,b-1)
        elif decision == "L":
            return (a-1,b)
        elif decision == "R":
            return (a+1,b)
        else:
            return (-1,-1)
    except:
        return (-1,-1)

# This function actually moves a player according to its decision and returns new info
def move(decision1, decision2, maze, player1_location, player2_location, stuck1, stuck2, moves1, moves2, miss1, miss2):
    cell1 = cell_of_decision(player1_location, decision1)
    cell2 = cell_of_decision(player2_location, decision2)
    if cell1 in maze[player1_location]:
        stuck1 = maze[player1_location][cell1]
        player1_location = cell1
        moves1 = moves1 + 1
    elif stuck1 <= 0:
        miss1 = miss1 + 1
    if cell2 in maze[player2_location]:
        stuck2 = maze[player2_location][cell2]
        player2_location = cell2
        moves2 = moves2 + 1
    elif stuck2 <= 0:
        miss2 = miss2 + 1
    return player1_location, player2_location, stuck1, stuck2, moves1, moves2, miss1, miss2

# This send the initial information about the game to a player
def initial_info(q, player1_location, player2_location, maze, pieces_of_cheese):
    q.put((maze, player1_location, player2_location, pieces_of_cheese))

# This send the chronic information about the game to a player
def send_turn(q, player1_location, player2_location, score1, score2, pieces_of_cheese):
    q.put((player1_location, player2_location, score1, score2, pieces_of_cheese))

# This function helps communicate with the user of the program, either through
# the graphical interface or command line
def send_info(text, q_info):
    if not(args.nodrawing):
        q_info.put(text)
    else:
        print(text, file=sys.stderr)

# This is the core function that runs a game. It takes the screen as argument
# and returns stats about the game
def run_game(screen, infoObject):
    
    global is_human_rat, is_human_python
    
    # Load saved match
    if args.load_match :
        args.rat = args.load_match + os.path.sep + [f for f in os.listdir(args.load_match) if f[:4] == "rat_"][0]
        args.python = args.load_match + os.path.sep + [f for f in os.listdir(args.load_match) if f[:7] == "python_"][0]
        args.maze_file = args.load_match + os.path.sep + "match_maze.maze"
    
    # Generate connected maze
    debug("Generating maze",1)
    if not(args.random_seed):
        random_seed = random.randint(0,sys.maxsize)
    else:
        random_seed = args.random_seed
    print("Using seed " + str(random_seed), file=sys.stderr)
    width, height, pieces_of_cheese, maze, player1_location, player2_location = generate_maze(args.width, args.height, args.density, not(args.nonconnected), not(args.nonsymmetric), args.mud_density, args.mud_range, args.maze_file, random_seed)
    if args.maze_file :
        args.pieces = len(pieces_of_cheese)
    
    # Generate cheese
    debug("Generating pieces of cheese",1)
    if args.random_cheese:
        random.seed()
    if pieces_of_cheese == []:
        pieces_of_cheese, player1_location, player2_location = generate_pieces_of_cheese(args.pieces, width, height, not(args.nonsymmetric), player1_location, player2_location, args.start_random)
    if args.save:
        savefile = open("saves" + os.path.sep +str(int(round(time.time() * 1000))),'w')
        savefile.write("# Random seed\n")
        savefile.write(str(random_seed)+"\n")
        savefile.write("# MazeMap\n")
        savefile.write(str(maze)+"\n")
        savefile.write("# Pieces of cheese\n")
        savefile.write(str(pieces_of_cheese)+"\n")
        savefile.write("# Rat initial location\n")
        savefile.write(str(player1_location)+"\n")
        savefile.write("# Python initial location\n")
        savefile.write(str(player2_location)+"\n")

        
    # Create communications queues with players
    debug("Generating pipes with players",1)
    q1_in = mp.Queue()
    q2_in = mp.Queue()
    q1_out = mp.Queue()
    q2_out = mp.Queue()
    q1_quit = mp.Queue()
    q2_quit = mp.Queue()

    # Instantiate players
    debug("Instantiating players",1)
    if not(is_human_rat):
        p1 = mp.Process(target=player, args=("rat", args.rat, q1_in, q1_out, q1_quit, width, height, args.preparation_time, args.turn_time,))
        p1.start()
    else:
        q1_out.put("human")
    if not(is_human_python):
        p2 = mp.Process(target=player, args=("python", args.python, q2_in, q2_out, q2_quit, width, height, args.preparation_time, args.turn_time,))
        p2.start()
    else:
        q2_out.put("human")

    # Initialize stats
    debug("Creating variables",1)
    score1 = 0
    score2 = 0
    stuck1 = 0
    stuck2 = 0

    moves1 = 0
    moves2 = 0
    miss1 = 0
    miss2 = 0
    stucks1 = 0
    stucks2 = 0         

    turns = 0
    win1 = 0
    win2 = 0
    
    preprocessing_over1 = False
    preprocessing_over2 = False
    still_computing1 = True
    still_computing2 = True
    
    
    # Retrieve names
    debug("Reading names of players",1)
    p1name = str(q1_out.get())
    p2name = str(q2_out.get())
    if args.load_match :
        p1name = p1name[4:]
        p2name = p2name[7:]

    # Prepare save match
    if args.save_match:
        savematch_dir = "saves" + os.path.sep + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        os.mkdir(savematch_dir)
        print("Match will be saved in directory", savematch_dir)
        savematch_p1 = open(savematch_dir + os.path.sep + "rat_" + p1name + ".py", 'w')
        savematch_p2 = open(savematch_dir + os.path.sep + "python_" + p2name + ".py", 'w')
        savematch_maze = open(savematch_dir + os.path.sep + "match_maze.maze", 'w')
        for f in [savematch_p1, savematch_p2] :
            f.write("turn_nb = 0\n\n")
            f.write("def preprocessing (maze_map, maze_width, maze_height, player_location, opponent_location, pieces_of_cheese, time_allowed) :\n")
            f.write("    pass\n\n")
            f.write("def turn (maze_map, maze_width, maze_height, player_location, opponent_location, player_score, opponent_score, pieces_of_cheese, time_allowed) :\n")
            f.write("    global turn_nb\n")
            f.write("    turn_nb += 1\n")
        savematch_maze.write(str(width) + "\n")
        savematch_maze.write(str(height) + "\n")
        for cell in range(width * height) :
            x, y = (cell % width, cell // width)
            savematch_maze.write(str(maze[(x, y)][(x, y+1)] if (x, y+1) in maze[(x, y)] else 0) + " ")
            savematch_maze.write(str(maze[(x, y)][(x, y-1)] if (x, y-1) in maze[(x, y)] else 0) + " ")
            savematch_maze.write(str(maze[(x, y)][(x-1, y)] if (x-1, y) in maze[(x, y)] else 0) + " ")
            savematch_maze.write(str(maze[(x, y)][(x+1, y)] if (x+1, y) in maze[(x, y)] else 0) + "\n")
        savematch_maze.write(str(player1_location[1] * width + player1_location[0]) + "\n")
        savematch_maze.write(str(player2_location[1] * width + player2_location[0]) + "\n")
        for cheese in pieces_of_cheese :
            savematch_maze.write(str(cheese[1] * width + cheese[0]))
            if cheese != pieces_of_cheese[-1] :
                savematch_maze.write(" ")

    # Start rendering
    debug("Starting rendering",1)
    q_render = Queue()
    q_render_in = Queue()
    q_info = Queue()
    if not(args.nodrawing):
        q_render_quit = Queue ()
        draw = Thread(target=run, args=(maze, width, height, q_render, q_render_in, q_render_quit, p1name, p2name, q1_out, q2_out, is_human_rat, is_human_python, q_info, pieces_of_cheese, player1_location, player2_location, args.rat != "", args.python != "", screen, infoObject))
        draw.start()

    # Send initial information to players
    debug("Send initial information to players and start preprocessing",1)
    initial_info(q1_in, player1_location, player2_location, maze, pieces_of_cheese)
    initial_info(q2_in, player2_location, player1_location, maze, pieces_of_cheese)

    # Let time to preprocess
    if not(args.synchronous):
        time.sleep(args.preparation_time / 1000.0)        

    # Main loop
    debug("Starting game",1)
    while 1:
    
    
        # First tell players if game is finished
        q1_quit.put(False)
        q2_quit.put(False)    

        # Check if too many turns have occured, this is mainly to avoid unending games
        if turns == args.max_turns:
            send_info("max number of turns reached!", q_info)
            break
        turns = turns + 1

        # Check if preprocessing is over
        if not preprocessing_over1 :
            try :
                decision1 = str(q1_out.get(args.synchronous))
                preprocessing_over1 = True
                still_computing1 = False
            except :
                pass
        if not preprocessing_over2 :
            try :
                decision2 = str(q2_out.get(args.synchronous))
                preprocessing_over2 = True
                still_computing2 = False
            except :
                pass

        # If players are stuck with mud, this is one turn towards getting out of it
        stuck1 = stuck1 - 1
        stuck2 = stuck2 - 1

        # Now check if one of the players is on a piece of cheese
        if player1_location in pieces_of_cheese and stuck1 <= 0 and args.rat != "":
            pieces_of_cheese.remove(player1_location)
            if player2_location == player1_location and stuck2 <= 0 and args.python != "":
                score1 = score1 + 0.5
                score2 = score2 + 0.5
                play_sound(effect_both)
            else:
                score1 = score1 + 1
                if player2_location in pieces_of_cheese and stuck2 <= 0 and args.python != "":
                    play_sound(effect_both)
                else:
                    play_sound(effect_left)
        if player2_location in pieces_of_cheese and stuck2 <= 0 and args.python != "":
            pieces_of_cheese.remove(player2_location)
            score2 = score2 + 1
            play_sound(effect_right)

        # Send drawing informations to graphical interface
        q_render.put((pieces_of_cheese.copy(), player1_location, player2_location, score1, score2, moves1, moves2, miss1, miss2, stucks1, stucks2))

        # Check if one of the players won
        if args.rat != "" and args.python != "":
            if score1 == score2 and score1 >= args.pieces / 2:
                send_info("The Rat(" + p1name + ") and the Python (" + p2name + ") got the same number of pieces of cheese!", q_info)
                break
            if score1 > args.pieces / 2:
                send_info("The Rat (" + p1name + ") won the match!", q_info)
                win1 = win1 + 1
                break
            if score2 > args.pieces / 2:
                send_info("The Python (" + p2name + ") won the match!", q_info)
                win2 = win2 + 1
                break
        else:
            if score1 >= args.pieces:
                send_info("The Rat (" + p1name + ") got all pieces of cheese!", q_info)
                win1 = win1 + 1
                break
            elif score2 >= args.pieces:
                send_info("The Python (" + p2name + ") got all pieces of cheese!", q_info)
                win2 = win2 + 1
                break
        # Or if there is no more cheese
        if len(pieces_of_cheese) == 0:
            send_info("No more pieces of cheese!", q_info)
            break

        # If players can move, ask them their next decision
        if stuck1 <= 0 and not still_computing1 :
            still_computing1 = True
            send_turn(q1_in, player1_location, player2_location, score1, score2, pieces_of_cheese)
        if stuck2 <= 0 and not still_computing2 :
            still_computing2 = True
            send_turn(q2_in, player2_location, player1_location, score2, score1, pieces_of_cheese)
        if args.save:
            savefile.write("# turn "+str(turns) + " rat_location then python_location then pieces_of_cheese then rat_decision then python_decision\n")
            savefile.write(str(player1_location) + "\n")
            savefile.write(str(player2_location) + "\n")
            savefile.write(str(pieces_of_cheese) + "\n")

        # Wait for the turn to end
        if not(args.synchronous):
            time.sleep(args.turn_time / 1000.0)

        # retrieve decisions from players
        try:
            if stuck1 <= 0:
                decision1 = str(q1_out.get(args.synchronous))
            else:
                decision1 = "None"
                stucks1 = stucks1 + 1
            still_computing1 = False
        except:
            decision1 = "None"
        try:
            if stuck2 <= 0:
                decision2 = str(q2_out.get(args.synchronous))
            else:
                decision2 = "None"
                stucks2 = stucks2 + 1
            still_computing2 = False
        except:
            decision2 = "None"

        if args.save:
            savefile.write(decision1 + "\n")
            savefile.write(decision2 + "\n")
            
        if args.save_match:
            if stuck1 <= 0 :
                savematch_p1.write("    if turn_nb == " + str(turns - stucks1) + ":\n")
                savematch_p1.write("        return '" + decision1 + "'\n")
            if stuck2 <= 0 :
                savematch_p2.write("    if turn_nb == " + str(turns - stucks2) + ":\n")
                savematch_p2.write("        return '" + decision2 + "'\n")
            
            
        # Check if graphical interface wants us to exit the game
        try:
            q_render_in.get(False)
            break
        except queue.Empty:
            ()

        # Magic solver for windows problems (does not like pygame in threads)
        if not(args.nodrawing) and not(args.save_images):
            pygame.event.pump()
        
        # Finally update informations about the game
        player1_location, player2_location, stuck1, stuck2, moves1, moves2, miss1, miss2 = move(decision1, decision2, maze, player1_location, player2_location, stuck1, stuck2, moves1, moves2, miss1, miss2)

    # Now the game is finished, send ending signals to players
    q1_quit.put(True)
    q2_quit.put(True)
    q1_in.put(True)
    q2_in.put(True)
    send_turn(q1_in, player1_location, player2_location, score1, score2, pieces_of_cheese)
    send_turn(q2_in, player2_location, player1_location, score2, score1, pieces_of_cheese)

    while 1:
        res = q1_out.get()
        try:
            if res:
                p1_prep_delay, p1_turn_delay = res
                break
        except:
            pass
        time.sleep(0.1)
    while 1:
        res = q2_out.get()
        try:
            if res:
                p2_prep_delay, p2_turn_delay = res
                break
        except:
            pass
        time.sleep(0.1)
        
    # Check if players are not waiting for info
    try:
        if p1.is_alive():
            try:
                for i in range(5):
                    q1_in.put(True)
            except:
                ()
        if p2.is_alive():
            try:
                for i in range(5):
                    q2_in.put(True)
            except:
                ()
        # If they are still not dead, ask them gently to stop
        time.sleep(0.1)
        if p1.is_alive():
            try:
                p1.terminate()
            except:
                ()
        if p2.is_alive():
            try:
                p2.terminate()
            except:
                ()
    except:
        ()
    time.sleep(0.1)
    # If they are still not dead, kill them
    try:
        while p1.is_alive() or p2.is_alive():
            if p1.is_alive():
                os.kill(p1.pid, signal.SIGKILL)
            if p2.is_alive():
                os.kill(p2.pid, signal.SIGKILL)
            time.sleep(0.01)
    except:
        ()
    # Stop the graphical interface as well
    if not(args.nodrawing):
        if args.auto_exit:
            q_render_quit.put("")
        #if draw.is_alive():
        #    q_render_in.get()
        while draw.is_alive() and q_render_in.empty():
            pygame.event.pump()
            time.sleep(0.1)
    # Send stats about the game
    stats = {"win_rat": win1, "win_python": win2, "score_rat": score1, "score_python": score2, "moves_rat": moves1, "moves_python": moves2, "miss_rat": miss1, "miss_python": miss2, "stucks_rat":stucks1, "stucks_python":stucks2, "prep_time_rat":p1_prep_delay, "prep_time_python":p2_prep_delay, "turn_time_rat":p1_turn_delay, "turn_time_python":p2_turn_delay}
    if args.save:
        savefile.write(str(stats))
        savefile.close()
    return stats

def main():
    # Start program
    debug("Starting pygame...")
    pygame.init()
    debug("Defining screen object...")
    if not(args.nodrawing):
        if not(args.save_images):
            infoObject = pygame.display.Info()
            image_icon = pygame.image.load("resources" + os.path.sep + "various" + os.path.sep + "pyrat.ico")
            pygame.display.set_icon(image_icon)
            pygame.display.set_caption("PyRat")
            if args.fullscreen:
                #screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
                screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.NOFRAME|pygame.FULLSCREEN)
                args.window_width = infoObject.current_w
                args.window_height = infoObject.current_h
            else:
                screen = pygame.display.set_mode((args.window_width, args.window_height), pygame.RESIZABLE)
        else:
            screen = pygame.surface.Surface((args.window_width, args.window_height))            
            infoObject = ""
    else:        
        screen = ""
        infoObject = ""        
    # Run first game
    debug("Starting first game")
    result = run_game(screen, infoObject)
    # Run other games (if any)
    for i in range(args.tests - 1):
        debug("Starting match number " + str(i))
        print("match " + str(i+2) + "/" + str(args.tests))
        new = run_game(screen, infoObject)
        debug("Aggregating stats")
        result = {x: result.get(x, 0) + new.get(x, 0) for x in set(result).union(new)}
    debug("Writing stats and exiting")
    result = {k: v / args.tests for k, v in result.items()}
    # Print stats and exit
    print("{")
    for key,value in sorted(result.items()):
        print("\t\"" + str(key) + "\": " + str(value))
    print("}")
    pygame.quit()

if __name__ == "__main__":
    #mp.set_start_method("spawn") # Add that if there is a weird bug with OSX...
    main()
