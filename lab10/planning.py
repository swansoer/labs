
#author1:
#author2:

from grid import *
from visualizer import *
import threading
from queue import PriorityQueue
import math
import cozmo
import time
import sys
import numpy as np 

from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps

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
    # First tried manhattan distance but wasn't good enough so did direct distance which makes sense since the robot came move diagonally   
    #return abs(current[0]-goal[0])+abs(current[1]-goal[1])
    return math.sqrt((current[0]-goal[0])**2+(current[1]-goal[1])**2)


def cell_to_pose(cell,scale,angle=None):
        if angle is not None:
            angle = degrees(angle)
        pose = cozmo.util.Pose(cell[0]*scale+scale/2,cell[1]*scale+scale/2,0,angle_z = angle)
        return pose

def pose_to_cell(pose,scale):
    x = int(round(pose.position.x/scale,0))
    y = int(round(pose.position.y/scale,0))
    #print("cube is at ",x,y)
    return (x,y)

def get_finish_from_pose(pose,scale):
    angle = pose.rotation.angle_z.degrees
    addition = None
    if angle > -45 and angle < 45:
        addition = (-1,0)
    elif angle > 45 and angle < 135:
        addition = (0,-1)
    elif  angle < -45 and angle > -135:
        addition = (0,1)
    else:
        addition = (1,0)
    
    block = pose_to_cell(pose,scale)
    return (block[0]+addition[0],block[1]+addition[1])

def get_angle(current, next):
    return np.rad2deg(np.arctan(float(next[1]-current[1])/float(next[0]-current[0])))
    
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
    #robot.pose = Pose(0,0,0,angle_z = degrees(0))
    scale = grid.getScale()
    start = grid.getStart()
    #print("Start %i,%i",start[0],start[1])
    #print("Scale %i",scale)
    #print(robot.pose)
    pose = cell_to_pose(start,scale,0)
    #print(pose)
    robot.go_to_pose(cell_to_pose(start,scale,0)).wait_for_completed()
    cubes_seen = set()
    while not stopevent.is_set():
        cube = None
        count = 0
        while(cube is None):
            try:
                cube = robot.world.wait_for_observed_light_cube(timeout=1)
            except Exception:
                robot.turn_in_place(cozmo.util.degrees(15)).wait_for_completed()
                count += 1
            if count >= 6:
                start = (start[0]+1,start[1]+1)
                grid.setStart(start)
                robot.go_to_pose(cell_to_pose(start,scale,0)).wait_for_completed()
                count = 0
        
        cubes_seen.add(cube.cube_id)
        finalanlge = cube.pose.rotation.angle_z.degrees
        robot.say_text("I see the cube").wait_for_completed()
        #print(cube.pose)
        block = pose_to_cell(cube.pose,scale)
        grid.addObstacle(block)
        finish = get_finish_from_pose(cube.pose,scale)
        grid.addGoal(finish)
        astar(grid,heuristic)
        
        
        newpath = True
        while newpath:
            newpath = False
            path = grid.getPath()
            last = path[0]
            for i in range(len(path)):
                angle = 0
                if i+1 < len(path):
                    angle = get_angle(path[i],path[i+1])
                robot.go_to_pose(cell_to_pose(path[i],scale,angle)).wait_for_completed()
                newcube = None
                try:
                    newcube = robot.world.wait_for_observed_light_cube(timeout=1)
                except Exception:
                    print("don't do anything")
                if newcube is not None and newcube.cube_id not in cubes_seen:
                    cubes_seen.add(newcube.cube_id)
                    robot.say_text("I found a new cube").wait_for_completed()
                    grid.setStart(path[i])
                    grid.addObstacle(pose_to_cell(newcube.pose,scale))
                    grid.clearPath()
                    grid.clearVisited()
                    astar(grid,heuristic)
                    newpath = True
                    break
            
            if not newpath:
                robotangle = robot.pose.rotation.angle_z.degrees
                robot.turn_in_place(cozmo.util.degrees(finalanlge-robotangle)).wait_for_completed()
        break
        stopevent.set()        
        
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

