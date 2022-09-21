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
        moves += find_route(traversal(start_position, maze_map), start_position, cheese_position)
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

def create_structure():
    """Create queuing structure"""
    return []

def push_to_structure(structure, element):
    """Push element to queuing structure"""
    structure.append(element)

def pop_from_structure(type, structure):
    """Pop element from queuing structure"""
    if type.upper() == "FIFO":
        return structure.pop(0)
    elif type.upper() == "LIFO":
        return structure.pop()
    else:
        raise Exception("Unknown structure type")

def traversal(start_vertex, graph):
    """Return routing table from the graph traversal starting from a vertex"""

    explored_vertices = []
    queue = []
    routing_table = {}
    distances = {}

    # We add the initial vertex to the queue
    heapq.heappush(queue, (0, start_vertex))
    distances[start_vertex] = 0
    routing_table[start_vertex] = None

    # While the exploring queue is not empty
    while len(queue) > 0:
        # We pop the first element
        cur_weight, cur_vertice = heapq.heappop(queue)
        explored_vertices.append(cur_vertice)

        # We add every unexplored neighbor to the queue
        #print("nei", list(graph[cur_vertice].items()))
        for (neighbor, edge_weight) in list(graph[cur_vertice].items()):
            total_weight = cur_weight + edge_weight
            if neighbor not in explored_vertices:
                heapq.heappush(queue, (total_weight, neighbor))
            if neighbor not in distances or total_weight < distances[neighbor]:
                routing_table[neighbor] = cur_vertice
                distances[neighbor] = total_weight

    return routing_table

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