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
from unittest.mock import patch

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

    #meta_graph, paths = build_meta_graph(maze_map, pieces_of_cheese+[player_location])
    #route = tsp(meta_graph, player_location)

    route, paths = greedy(maze_map, player_location, pieces_of_cheese+[player_location])

    print("route", route)
    #Calculation all paths to get every piece of cheese
    for position_id in range(len(route)-1):
        # We add direction instruction to the queue of movements (FIFO)
        # We calculate path from a piece of cheese to the next one in the list
        moves += paths[route[position_id]][route[position_id+1]]
    

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
    if len(moves) > 0:
        turn = moves.pop(0)
        print(f"[LOG] Decision : {turn}")
        return turn
    else:
        print("[LOG] Pas de mouvement !")
        return MOVE_DOWN


##############################################################

#                       OTHER FUNCTIONS

##############################################################

def traversal(start_vertex, graph):
    """Return routing table from the graph traversal starting from a vertex using Dijkstra’s algorithm"""

    explored_vertices = [] # Contains the list of explored vertices
    queue = [] # Priority queue of traversal, contains only unexplored vertices
    routing_table = {} # Dict that will contains the routing table
    distances = {} # Dict of current distances to all other vertices.
    # Distance to a vertice not in the dict is infinity

    # We add the initial vertex to the queue and set its distance to 0
    heapq.heappush(queue, (0, start_vertex))
    distances[start_vertex] = 0
    routing_table[start_vertex] = None # No parent for initial vertice

    # While the exploring queue is not empty
    while len(queue) > 0:

        # We pop the unexplored vertice with lowest distance
        cur_weight, cur_vertice = heapq.heappop(queue)
        explored_vertices.append(cur_vertice)

        for neighbor in graph[cur_vertice]:
            # We calculate the new total weight from initial vertice
            total_weight = cur_weight + graph[cur_vertice][neighbor]

            # We add every unexplored neighbor to the queue if not yet explored
            if neighbor not in explored_vertices and (total_weight, neighbor) not in queue:
                heapq.heappush(queue, (total_weight, neighbor))
            
            # We set the new distance if its lower than the previous one
            if neighbor not in distances or total_weight < distances[neighbor]:
                routing_table[neighbor] = cur_vertice # This is the closest parent for now
                distances[neighbor] = total_weight

    # We return the routing table (representing the shortest path)
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


def build_meta_graph (maze_map, locations) :
    """Return the meta-graph and all necessary routing tables"""
    graph = {}
    paths = {}
    for cur_loc in locations:
        routing_table, distances = traversal(cur_loc, maze_map)
        graph[cur_loc] = {}            
        paths_from_loc = {}
        for cur_dest in locations:
            if cur_dest != cur_loc:
                graph[cur_loc][cur_dest] = distances[cur_dest]
                paths_from_loc[cur_dest] = find_route(routing_table, cur_loc, cur_dest)
        paths[cur_loc] = paths_from_loc
    return graph, paths

def tsp (graph, initial_vertex) :
    """Solve the TSP using a exhaustive backtracking strategy"""
    
    best_length = 9e99
    best_route = []

    # Recursive implementation of a depth-first search
    def _tsp (current_vertex, current_length, visited_vertices) :
        nonlocal best_length
        nonlocal best_route

        if current_length >= best_length:
            return

        cur_visited_vertices = visited_vertices.copy()

        # Visiting a vertex
        #print("Visiting", current_vertex, "at distance", current_length, "from start. Explored :",cur_visited_vertices)
        cur_visited_vertices.append(current_vertex)
        
        # We stop when all vertices are visited
        if len(cur_visited_vertices) == len(graph) :
            if current_length < best_length:
                best_length = current_length
                best_route = cur_visited_vertices
                #print(best_length, best_route)
            return 
        
        # If there are still vertices to visit, we explore unexplored neighbors
        for neighbor in graph[current_vertex] :
            if neighbor not in cur_visited_vertices :
                _tsp(neighbor, current_length + graph[current_vertex][neighbor], cur_visited_vertices)
                
        # If there are no unvisited neighbors left, the inner function will return,
        # which corresponds to coming back to the previously visited vertex
        
    # Initial call
    _tsp(initial_vertex, 0, [])
    return best_route

def give_score (graph, current_vertex, neighbors) :
    # Associate a score (length of path) to each given neighbor
    scores = {}
    for loc in neighbors:
        scores[loc] = graph[current_vertex][loc]
    return scores

def greedy (graph, initial_vertex, vertices_to_visit) :
    # Greedy algorithm that goes to the score minimizer until all vertices are visited
    meta_graph, paths = build_meta_graph(graph, vertices_to_visit)
    global_path = [initial_vertex]
    explored_vertices = [initial_vertex]
    cur_vertex = initial_vertex
    while not len(explored_vertices) == len(meta_graph):
        score = give_score(meta_graph, cur_vertex, [x for x in meta_graph[cur_vertex].keys() if x not in explored_vertices])
        nearest = min(score, key=score.get)
        explored_vertices.append(nearest)
        global_path.append(nearest)
        cur_vertex = nearest
    return global_path, paths
