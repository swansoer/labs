#!/usr/bin/env python3

'''
This is starter code for Lab 7.

'''

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
import math
import time
import sys

from odometry import cozmo_go_to_pose
from odometry import my_go_to_pose1
from odometry import my_go_to_pose2
from odometry import my_go_to_pose3
sys.path.insert(0, '../lab6')
from pose_transform import get_relative_pose

def move_relative_to_cube(robot: cozmo.robot.Robot):
    '''Looks for a cube while sitting still, when a cube is detected it 
    moves the robot to a given pose relative to the detected cube pose.'''

    robot.move_lift(-3)
    robot.set_head_angle(degrees(0)).wait_for_completed()
    cube = None
    relative_pose = None
    
    while cube is None:
        try:
            cube = robot.world.wait_for_observed_light_cube(timeout=30)
            if cube:
                relative_pose = get_relative_pose(cube.pose, robot.pose)
                print("Found a cube, pose in the robot coordinate frame: %s" % relative_pose)
        except asyncio.TimeoutError:
            print("Didn't find a cube")

    desired_pose_relative_to_cube = Pose(0*math.sin(cube.pose.rotation.angle_z.radians), 100*math.cos(cube.pose.rotation.angle_z.radians), 0, angle_z=degrees(90))
    final_pose = cube.pose + desired_pose_relative_to_cube
    print("Found a point, pose in the robot coordinate frame: %s" % final_pose)
    relative_pose = get_relative_pose(final_pose, robot.pose)
    print("Found a relative pose, pose in the robot coordinate frame: %s" % relative_pose)
    my_go_to_pose3(robot, relative_pose.position.x, relative_pose.position.y, relative_pose.rotation.angle_z.degrees)
    
    # ####
    # TODO: Make the robot move to the given desired_pose_relative_to_cube.
    # Use the get_relative_pose function your implemented to determine the
    # desired robot pose relative to the robot's current pose and then use
    # one of the go_to_pose functions you implemented in Lab 6.
    # ####


if __name__ == '__main__':

    cozmo.run_program(move_relative_to_cube)
