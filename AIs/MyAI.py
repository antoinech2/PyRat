# Import of random module
import random
MOVE_DOWN = 'D'
MOVE_LEFT = 'L'
MOVE_RIGHT = 'R'
MOVE_UP = 'U'

Move_list = {(0,-1):MOVE_DOWN,(-1,0):MOVE_LEFT,(1,0):MOVE_RIGHT,(0,1):MOVE_UP}
visited_locations = []
moves = []
def random_move(maze_map,player_location):
    global visited_locations
    all_moves = [MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP]
    Neighbors = maze_map[player_location]
    possible_move = [Move_list[(i[0]-player_location[0],i[1]-player_location[1])] for i in Neighbors if i not in visited_locations]
    if len(possible_move) == 0:
        return random.choice([Move_list[(i[0]-player_location[0],i[1]-player_location[1])] for i in Neighbors])
    return random.choice(possible_move)
def preprocessing (maze_map, maze_width, maze_height, player_location, opponent_location, pieces_of_cheese, time_allowed) :
    print(pieces_of_cheese)
    moves_from_locations([pieces_of_cheese[0]]+find_route(traversal(player_location,maze_map)[1],player_location,pieces_of_cheese[0]))
    # Nothing to do here
    pass
def turn (maze_map, maze_width, maze_height, player_location, opponent_location, player_score, opponent_score, pieces_of_cheese, time_allowed) :
    
    # Returns a random move each turn
    global moves
    print(len(moves))
    move = moves[0]
    moves = moves[1:]
    return move
    
def create_structure () :
    # Create an empty FIFO
    global fifo
    fifo = []
    
def push_to_structure (structure, element) :
    # Add an element to the FIFO
    structure.append(element)
    return structure
def pop_from_structure (structure) :
    # Extract an element from the FIFO
    return structure[0],structure[1:]
def traversal (start_vertex, graph) :
    fifo = []
    fifo = push_to_structure(fifo,(start_vertex, None))
    explored_vertices = []
    routing_table = {}
    while len(fifo)>0:
        (current_vertex,parent),fifo = pop_from_structure(fifo)
        if current_vertex not in explored_vertices:
            explored_vertices.append(current_vertex)
            routing_table[current_vertex] = parent
            for neighbors in graph[current_vertex]:
                if neighbors not in explored_vertices:
                    fifo = push_to_structure(fifo,(neighbors,current_vertex))
    return explored_vertices,routing_table
def find_route(routing_table, source_location,target_location): 
    print(routing_table)
    route = [routing_table[target_location]]
    while routing_table[route[len(route)-1]] != None:
        route.append(routing_table[route[-1]])
    return route
    
def moves_from_locations(locations):
    global moves
    n = len(locations)-1
    for i in range(n):
        print(i,' ****************')
        moves.append(Move_list[(locations[i][0]-locations[i+1][0],locations[i][1]-locations[i+1][1])])
    moves.reverse()
    print(moves)