
#author1:
#author2:

from grid import *
from visualizer import *
import threading
from queue import PriorityQueue
import math
import cozmo



def astar(grid, heuristic):
    """Perform the A* search algorithm on a defined grid

        Arguments:
        grid -- CozGrid instance to perform search on
        grid -- CozGrid instance to perform search on
        heuristic -- supplied heuristic function
    """
    evaluatedMap = {}
    unevaluatedMap = {}
    start = grid.getStart()
    goal = grid.getGoals()[0]
    startG = 0
    startH = heuristic(start,goal)
    currentNode = Node(start,startH,startG)
    unevaluatedMap[currentNode.coord] = currentNode
    
    while len(unevaluatedMap) > 0:
        # I tried using a PriorityQueue but because a node could end up with 
        # an updated priority it really didn't make sense to use one and
        # instead had to just serach the dictionary each time for the smallest
        # priority which is the sum of g and h
        currentNode = min(unevaluatedMap.values(),key=lambda x:x.g + x.h)
        
        # if the current node is the goal then create the path by iterating backwards
        # and pushing the current node to the front of the path and then moving to the
        # parent node
        if currentNode.coord == goal:
            path = []
            while currentNode.parentNode:
                path.insert(0,currentNode.coord)
                currentNode = currentNode.parentNode
            path.insert(0,currentNode.coord)
            grid.setPath(path)
            return
            
        # Move the current node to the evaluated map and delete it from
        # the unevaluated map
        evaluatedMap[currentNode.coord] = currentNode
        del unevaluatedMap[currentNode.coord]
        
        # Mark the current node as having been visited
        grid.addVisited(currentNode.coord)
        
        # Get the neighbors of the current node
        neighbors = grid.getNeighbors(currentNode.coord)

        # For each neighbor check if that neighbor has alread been evaluated
        # if it has then skip that neighbor.  If it hasn't and it isn't in the
        # unevaluated map add it with a high cost and heuristic.
        # Get the neighbor from the unevaluated map and calculate the current
        # cost.  If the current cost is less than what existed update the neighbor
        # and add it back to the list otherwise skip to next neighbor
        for neighbor in neighbors:
            ncoord = (neighbor[0])
            if (ncoord) in evaluatedMap:
                continue
            if (ncoord) not in unevaluatedMap:
                node = Node(ncoord,float('inf'),float('inf'))
                unevaluatedMap[ncoord] = node
            
            node = unevaluatedMap[ncoord]
            calc_cost = currentNode.g + neighbor[1]
            if calc_cost >= node.g:
                continue
                
            node.parentNode = currentNode
            node.g = calc_cost
            node.h = heuristic(ncoord,goal)


def heuristic(current, goal):
    """Heuristic function for A* algorithm

        Arguments:
        current -- current cell
        goal -- desired goal cell
    """
    # First tried manhattan distance but wasn't good enough so did direct distance    
    #return abs(current[0]-goal[0])+abs(current[1]-goal[1])
    return math.sqrt((current[0]-goal[0])**2+(current[1]-goal[1])**2)


def cozmoBehavior(robot: cozmo.robot.Robot):
    """Cozmo search behavior. See assignment description for details

        Has global access to grid, a CozGrid instance created by the main thread, and
        stopevent, a threading.Event instance used to signal when the main thread has stopped.
        You can use stopevent.is_set() to check its status or stopevent.wait() to wait for the
        main thread to finish.

        Arguments:
        robot -- cozmo.robot.Robot instance, supplied by cozmo.run_program
    """
        
    global grid, stopevent
    
    while not stopevent.is_set():
        pass # Your code here


        
class Node:
    def __init__(self, coord,h=0,g=0):
        self.coord = coord
        self.h = h
        self.g = g
        self.parentNode = None
######################## DO NOT MODIFY CODE BELOW THIS LINE ####################################


class RobotThread(threading.Thread):
    """Thread to run cozmo code separate from main thread
    """
        
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

    def run(self):
        cozmo.run_program(cozmoBehavior)


# If run as executable, start RobotThread and launch visualizer with empty grid file
if __name__ == "__main__":
    global grid, stopevent
    stopevent = threading.Event()
    grid = CozGrid("emptygrid.json")
    visualizer = Visualizer(grid)
    updater = UpdateThread(visualizer)
    updater.start()
    robot = RobotThread()
    robot.start()
    visualizer.start()
    stopevent.set()

