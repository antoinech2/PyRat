##############################################################
# The turn function should always return a move to indicate where to go
# The four possibilities are defined here
##############################################################

MOVE_DOWN = 'D'
MOVE_LEFT = 'L'
MOVE_RIGHT = 'R'
MOVE_UP = 'U'

##############################################################
# Please put your code here (imports, variables, functions...)
##############################################################
import heapq
import time

##############################################################
# The preprocessing function is called at the start of a game
# It can be used to perform intensive computations that can be
# used later to move the player in the maze.
# ------------------------------------------------------------
# maze_map : dict(pair(int, int), dict(pair(int, int), int))
# maze_width : int
# maze_height : int
# player_location : pair(int, int)
# opponent_location : pair(int,int)
# pieces_of_cheese : list(pair(int, int))
# time_allowed : float
##############################################################

def preprocessing (maze_map, maze_width, maze_height, player_location, opponent_location, pieces_of_cheese, time_allowed) :
    global moves
    moves = []
    start_position = player_location

    #Calculation all paths to get every piece of cheese
    for cheese_position in pieces_of_cheese:
        # We add direction instruction to the queue of movements (FIFO)
        # We calculate path from a piece of cheese to the next one in the list
        moves += find_route(traversal(start_position, maze_map)[0], start_position, cheese_position)
        start_position = cheese_position
    

##############################################################
# The turn function is called each time the game is waiting
# for the player to make a decision (a move).
# ------------------------------------------------------------
# maze_map : dict(pair(int, int), dict(pair(int, int), int))
# maze_width : int
# maze_height : int
# player_location : pair(int, int)
# opponent_location : pair(int,int)
# player_score : float
# opponent_score : float
# pieces_of_cheese : list(pair(int, int))
# time_allowed : float
##############################################################

def turn (maze_map, maze_width, maze_height, player_location, opponent_location, player_score, opponent_score, pieces_of_cheese, time_allowed) :
    # We pop and execute the move
    turn = moves.pop(0)
    print(f"[LOG] Decision : {turn}")
    return turn


##############################################################

#                       OTHER FUNCTIONS

##############################################################

def add_or_replace(queue, element):
    """Add the element to the queue or replace it if the value is lower than the one in the queue"""
    for cur_elem in queue:
        # Si on trouve l'élément déjà existant
        if cur_elem[1] == element[1]:
            if element[0] < cur_elem[0]:
                # S'il a une valeur plus faible, alors on le remplace 
                # On supprime l'ancien élément et on push dans la queue
                queue.remove(cur_elem)
                heapq.heappush(queue, element)
            return #Il ne peut y avoir qu'une seule fois l'élement, on met fin à la boucle
    heapq.heappush(queue, element) #Si l'élement n'est pas quand la queue, on l'ajoute

def traversal(start_vertex, graph):
    """Return routing table from the graph traversal starting from a vertex"""

    explored_vertices = []
    queue = []
    routing_table = {}
    distances = {}

    # We add the initial vertex to the queue
    add_or_replace(queue, (0, start_vertex))
    distances[start_vertex] = 0
    routing_table[start_vertex] = None

    # While the exploring queue is not empty
    while len(queue) > 0:
        # We pop the first element
        cur_weight, cur_vertice = heapq.heappop(queue)

        if cur_vertice not in explored_vertices:
        # We add every unexplored neighbor to the queue
            for neighbor in graph[cur_vertice]:
                total_weight = cur_weight + graph[cur_vertice][neighbor]
                add_or_replace(queue, (total_weight, neighbor))
                if neighbor not in distances or total_weight < distances[neighbor]:
                    routing_table[neighbor] = cur_vertice
                    distances[neighbor] = total_weight
            explored_vertices.append(cur_vertice)

    return routing_table, distances

def get_direction_from_neighbors_location(source_location, target_location):
    """Get the direction to go from a location to another adjacent location"""
    move_list = {(0,-1) : MOVE_DOWN, (-1,0) : MOVE_LEFT, (1,0) : MOVE_RIGHT, (0,1) : MOVE_UP}
    return move_list[(target_location[0]-source_location[0],target_location[1]-source_location[1])]


def find_route (routing_table, source_location, target_location) :
    """Return list of moves to go from source to target"""
    result_path = []

    child = target_location
    parent = routing_table[child]

    # We go through the routing table starting from the target until we found the source
    while not child == source_location:
        # We determine the direction to go from the parent to the child, and add it as the first move
        result_path.insert(0, get_direction_from_neighbors_location(parent, child))

        # We redefine the new child and parent
        child = parent
        parent = routing_table[child]
    
    return result_path