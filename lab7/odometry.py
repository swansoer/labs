#!/usr/bin/env python3

'''
Stater code for Lab 7.

'''

import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
import math
import time as timer
import numpy as np

# Wrappers for existing Cozmo navigation functions

###
# Note: because of lots of slippage of wheels I had to add some constants that don't necessarily make sense
# such as time*3 for turn in place.  The wheels while spinning go much slower than specified vs when both are moving forward
# so the set velocity*duration value doesn't match what you would expect
##

def cozmo_drive_straight(robot, dist, speed):
    """Drives the robot straight.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        dist -- Desired distance of the movement in millimeters
        speed -- Desired speed of the movement in millimeters per second
    """
    robot.drive_straight(distance_mm(dist), speed_mmps(speed)).wait_for_completed()

def cozmo_turn_in_place(robot, angle, speed):
    """Rotates the robot in place.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        angle -- Desired distance of the movement in degrees
        speed -- Desired speed of the movement in degrees per second
    """
    robot.turn_in_place(degrees(angle), speed=degrees(speed)).wait_for_completed()

def cozmo_go_to_pose(robot, x, y, angle_z):
    """Moves the robot to a pose relative to its current pose.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        x,y -- Desired position of the robot in millimeters
        angle_z -- Desired rotation of the robot around the vertical axis in degrees
    """
    robot.go_to_pose(Pose(x, y, 0, angle_z=degrees(angle_z)), relative_to_robot=True).wait_for_completed()

# Functions to be defined as part of the labs

def get_front_wheel_radius():
    """Returns the radius of the Cozmo robot's front wheel in millimeters."""
    # ####
    # I found this by using the drive straight method.  I specified different values in mm to determine
    # how many mm it was to get 1 full rotation of the front wheel.  That told me the circumference of the
    # front wheel so the radius was just that number (85mm) divided by 2pi. (See measures.py)
    # ####
    return 13.53

def get_distance_between_wheels():
    """Returns the distance between the wheels of the Cozmo robot in millimeters."""
    # ####
    # I first did this empirically by spinning cozmo about one wheel creating an arch.  I set one wheel speed to 
    # 0 the other to 85 and played around with duration until I had cozmo do one exact circle.  I then used the speed
    # and duration to calculate a circumference then found the radius where the radius would be the distance
    # between wheels.  While this would be a fair way to find the value in theory in practice it was terrible.  THe
    # slippage that occurs while rotating around one wheel as well as the fact that the speed did not seem at all accurate
    # compared to when both wheels were running gave me a terrible estimate of the spacing (108mm).  Ultimately I used a ruler
    # ####
    return 47

def rotate_front_wheel(robot, angle_deg):
    """Rotates the front wheel of the robot by a desired angle.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        angle_deg -- Desired rotation of the wheel in degrees
    """

    radius = get_front_wheel_radius()
    speed = 85
    if angle_deg < 0:
        speed = speed * -1
        angle_deg = angle_deg * -1
    distance = radius*math.radians(angle_deg)
    time = distance/speed
    robot.drive_wheels(speed, speed, duration=time)

def my_drive_straight(robot, dist, speed):
    """Drives the robot straight.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        dist -- Desired distance of the movement in millimeters
        speed -- Desired speed of the movement in millimeters per second
    """
    # ####
    time = dist/speed
    if time < 0:
        time = time * -1
    robot.drive_wheels(speed, speed, duration = time)

def my_turn_in_place(robot, angle, speed):
    """Rotates the robot in place.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        angle -- Desired distance of the movement in degrees
        speed -- Desired speed of the movement in degrees per second
    """

    #print("angle %s speed %s", angle, speed)
    arclength = math.fabs(math.radians(angle))*get_distance_between_wheels()/2
    #print("arclength %s", arclength)
    time = arclength/speed
    #print("time %s" ,time)
    if math.radians(angle) < 0:
        speed = speed * -1
    
    robot.drive_wheels(-1*speed, speed, duration = 3*time)

def my_go_to_pose1(robot, x, y, angle_z):
    """Moves the robot to a pose relative to its current pose.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        x,y -- Desired position of the robot in millimeters
        angle_z -- Desired rotation of the robot around the vertical axis in degrees
    """

    angle_loc = math.degrees(math.atan(y/x))
    my_turn_in_place(robot, angle_loc, 15)
    timer.sleep(.2)
    distance = math.hypot(x,y)
    my_drive_straight(robot,distance,55)
    timer.sleep(.2)
    my_turn_in_place(robot, angle_z-angle_loc, 15)
    
def my_go_to_pose2(robot, x, y, angle_z):
    """Moves the robot to a pose relative to its current pose.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        x,y -- Desired position of the robot in millimeters
        angle_z -- Desired rotation of the robot around the vertical axis in degrees
    """

    time = 8
    theta = math.radians(angle_z)
    b = get_distance_between_wheels()
    r = get_front_wheel_radius()
    x_dot = time*x
    y_dot = time*y
    theta_dot = time*theta
    phi_dot_l = (2*x_dot - theta_dot*b)/(2*r*math.pi)
    phi_dot_r = (2*x_dot + theta_dot*b)/(2*r*math.pi)
    
    robot.drive_wheels(phi_dot_l, phi_dot_r, duration = time)

def my_go_to_pose3(robot, x, y, angle_z):
    """Moves the robot to a pose relative to its current pose.
        Arguments:
        robot -- the Cozmo robot instance passed to the function
        x,y -- Desired position of the robot in millimeters
        angle_z -- Desired rotation of the robot around the vertical axis in degrees
    """

    angle_loc = math.degrees(math.atan(y/x))
    my_turn_in_place(robot, angle_loc, 30)
    timer.sleep(.2)
    time = 8
    theta = math.radians(angle_z-angle_loc)
    b = get_distance_between_wheels()
    r = get_front_wheel_radius()
    x_dot = time*x
    y_dot = time*y
    theta_dot = time*theta
    phi_dot_l = (2*x_dot - theta_dot*b)/(2*r*math.pi)
    phi_dot_r = (2*x_dot + theta_dot*b)/(2*r*math.pi)
    
    robot.drive_wheels(phi_dot_l, phi_dot_r, duration = time)

def run(robot: cozmo.robot.Robot):

    print("***** Front wheel radius: " + str(get_front_wheel_radius()))
    print("***** Distance between wheels: " + str(get_distance_between_wheels()))

    ## Example tests of the functions

    cozmo_drive_straight(robot, 62, 50)
    cozmo_turn_in_place(robot, 60, 30)
    cozmo_go_to_pose(robot, 100, 100, 45)

    rotate_front_wheel(robot, 90)
    my_drive_straight(robot, 62, 50)
    my_turn_in_place(robot, 90, 30)

    my_go_to_pose1(robot, 100, 100, 45)
    my_go_to_pose2(robot, 100, 100, 45)
    my_go_to_pose3(robot, 100, 100, 45)


if __name__ == '__main__':

    cozmo.run_program(run)



