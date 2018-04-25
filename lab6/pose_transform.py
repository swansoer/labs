#!/usr/bin/env python3

'''
This is starter code for Lab 6 on Coordinate Frame transforms.

'''

import asyncio
import cozmo
import numpy as np
from cozmo.util import degrees
import time

# def get_relative_pose(object_pose, reference_frame_pose):

    # #theta = object_pose.rotation.angle_z.radians + reference_frame_pose.rotation.angle_z.radians
    # #x = object_pose.position.x + reference_frame_pose.position.x
    # #y = object_pose.position.y + reference_frame_pose.position.y
    # #z = object_pose.position.z + reference_frame_pose.position.z
    # #return cozmo.util.Pose(x,y,z,angle_z=cozmo.util.radians(theta))
    
    # #theta = object_pose.rotation.angle_z.radians - reference_frame_pose.rotation.angle_z.radians
    # #transform = np.matrix([[np.cos(theta), -1*np.sin(theta) ,0, object_pose.position.x],[np.sin(theta), np.cos(theta), 0, object_pose.position.y],[0, 0, 1, object_pose.position.z],[0, 0, 0, 1]])
    # #object = np.matrix([[reference_frame_pose.position.x],[reference_frame_pose.position.y],[reference_frame_pose.position.z],[0]])
    # #out = transform * object
    
    
    # #theta = reference_frame_pose.rotation.angle_z.radians - object_pose.rotation.angle_z.radians
    # theta = object_pose.rotation.angle_z.radians - reference_frame_pose.rotation.angle_z.radians
    # transform = np.matrix([[np.cos(theta), np.sin(theta) ,0, reference_frame_pose.position.x],[-1*np.sin(theta), np.cos(theta), 0, reference_frame_pose.position.y],[0, 0, 1, reference_frame_pose.position.z],[0, 0, 0, 1]])
    # object = np.matrix([[object_pose.position.x],[object_pose.position.y],[object_pose.position.z],[0]])
    # out = transform * object
    
    # return cozmo.util.Pose(out[0],out[1],out[2],angle_z=cozmo.util.radians(theta))
    

    
def get_relative_pose(object_pose, reference_frame_pose):

    theta_0_1 = reference_frame_pose.rotation.angle_z.radians
    p_01 = reference_frame_pose.position
    theta_0_2 = object_pose.rotation.angle_z.radians
    p_02 = object_pose.position
    transform_0_1 = np.matrix([[np.cos(theta_0_1), -1*np.sin(theta_0_1) ,0, p_01.x],[np.sin(theta_0_1), np.cos(theta_0_1), 0, p_01.y],[0, 0, 1, p_01.z],[0, 0, 0, 1]])
    transform_0_2 = np.matrix([[np.cos(theta_0_2), -1*np.sin(theta_0_2) ,0, p_02.x],[np.sin(theta_0_2), np.cos(theta_0_2), 0, p_02.y],[0, 0, 1, p_02.z],[0, 0, 0, 1]])
    transform_1_2 = np.linalg.inv(transform_0_1)*transform_0_2
    
    return cozmo.util.Pose(transform_1_2.item(0,3),transform_1_2.item(1,3),transform_1_2.item(2,3),angle_z=cozmo.util.radians(theta_0_2-theta_0_1))
    
    
def find_relative_cube_pose(robot: cozmo.robot.Robot):
    '''Looks for a cube while sitting still, prints the pose of the detected cube
    in world coordinate frame and relative to the robot coordinate frame.'''

    robot.move_lift(-3)
    robot.set_head_angle(degrees(0)).wait_for_completed()
    cube = None

    try:
        while True:
            try:
                cube = robot.world.wait_for_observed_light_cube(timeout=30)
                if cube:
                    print("Robot pose: %s" % robot.pose)
                    print("Cube pose: %s" % cube.pose)
                    pose1 = robot.pose.define_pose_relative_this(cube.pose)
                    print("Cube pose in the robot coordinate frame: %s" % pose)

            except asyncio.TimeoutError:
                print("Didn't find a cube")

    except KeyboardInterrupt:
        print("")
        print("Exit requested by user")

if __name__ == '__main__':

    cozmo.run_program(find_relative_cube_pose)
