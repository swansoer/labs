from grid import *
from particle import Particle
from utils import *
from setting import *
from random import randint
import numpy as np
import bisect
import math

sigma_inv = np.linalg.inv(np.matrix([[MARKER_TRANS_SIGMA**2,            0 ,                0],\
                                     [0,                     MARKER_TRANS_SIGMA**2,       0],\
                                     [0,                            0,                math.radians(MARKER_ROT_SIGMA)**2]]))

##
# This method takes a point in the origin frame as well as a relative measurement
# it applies the rotation matrix to the relative point to get to the origin
# frame, adds it to the origin frame point and then adjusts the orientation.
# It then returns a new particle that has the new calculatred x,y,h                                      
#
def add_relative_to_origin_frame(origin_point, relative):
    old_x,old_y,old_h = origin_point.xyh
    theta = math.radians(old_h)
    rotation = np.matrix([[np.cos(theta), -1*np.sin(theta), old_x], \
                          [np.sin(theta), np.cos(theta), old_y], \
                          [ 0 ,                0,          1]])
    relative_point = np.matrix([[relative[0]],\
                                [relative[1]],\
                                [1]])
    new_in_orgin_frame = rotation*relative_point
    return Particle(new_in_orgin_frame.item(0,0),new_in_orgin_frame.item(1,0),add_heading_deg(old_h,relative[2]))
    
def motion_update(particles, odom):
    """ Particle filter motion update

        Arguments: 
        particles -- input list of particle represents belief p(x_{t-1} | u_{t-1})
                before motion update
        odom -- odometry to move (dx, dy, dh) in *robot local frame*

        Returns: the list of particles represents belief \tilde{p}(x_{t} | u_{t})
                after motion update
    """
    ##
    # Here I will loop over each of the particles in the list
    # I will then apply the odom movement to the particle and pick a new particle out 
    # of a distribution at that point and add it to the motion_particles
    ##
    #print(particles)
    motion_particles = []
    num_particles = len(particles)
    sigma = 0
    print("odom: ",odom)
    for particle in particles:
        new_particle = add_relative_to_origin_frame(particle, odom)
        new_particle.x = add_gaussian_noise(new_particle.x,ODOM_TRANS_SIGMA)
        new_particle.y = add_gaussian_noise(new_particle.y,ODOM_TRANS_SIGMA)
        new_particle.h = add_gaussian_noise(new_particle.h,ODOM_HEAD_SIGMA)
        motion_particles.append(new_particle)
    return motion_particles

# ------------------------------------------------------------------------
def measurement_update(particles, measured_marker_list, grid):
    """ Particle filter measurement update

        Arguments: 
        particles -- input list of particle represents belief \tilde{p}(x_{t} | u_{t})
                before meansurement update (but after motion update)

        measured_marker_list -- robot detected marker list, each marker has format:
                measured_marker_list[i] = (rx, ry, rh)
                rx -- marker's relative X coordinate in robot's frame
                ry -- marker's relative Y coordinate in robot's frame
                rh -- marker's relative heading in robot's frame, in degree

                * Note that the robot can only see markers which is in its camera field of view,
                which is defined by ROBOT_CAMERA_FOV_DEG in setting.py
                * Note that the robot can see mutliple markers at once, and may not see any one

        grid -- grid world map, which contains the marker information, 
                see grid.py and CozGrid for definition
                Can be used to evaluate particles

        Returns: the list of particles represents belief p(x_{t} | u_{t})
                after measurement update
    """
    
    # If there were no sensed markers then skip the sensing update step and return original list of particles
    if len(measured_marker_list) == 0:
        return particles
        
    measured_particles = []
    all_w = []
    # loop through each particle
    for particle in particles:
        # if the particle isn't in the grid or not in a free space it has 0% weighting
        if not grid.is_free(particle.x,particle.y):
            all_w.append(0)
        else:
            w=0
            # for each measured marker find max probability the particle is relative to
            # one of the actual markers
            for measured in measured_marker_list:
                point = add_relative_to_origin_frame(particle, measured)
                weights = []
                for marker in grid.markers:
                    weights.append( prob_estimate(point, marker))
                w += max(weights)
            all_w.append(w)
                    
                                
    sum_w = sum(all_w)
    
    # normalize all the weights so they sum to one
    normalized_ws = [(w / sum_w) for w in all_w]
    
    # create an accumulation array from the weights of the particles
    accumulation = 0.0
    distribution = []
    for normalized_w in normalized_ws:
        accumulation += normalized_w
        distribution.append(accumulation)
    
    # Figure out what 95% of the total num of particles are
    num_particles = len(particles)
    subset = int(num_particles*.95)

    # pick 95% of the particles based on weight
    for _ in range(subset):
        randomselection = random.uniform(0,1)
        i=bisect.bisect_left(distribution, randomselection)
        measured_particles.append(particles[i])
    
    # Create 5% new particles that are random
    new_particles = Particle.create_random(num_particles - subset, grid)
    for p in new_particles:
        measured_particles.append(p)
    
    return measured_particles

##
# A method that does a gaussian pdf calc on the point relative to the actual
# location of the marker in x,y, and h degrees using the marker signmas for variance.
# If a point is very close to the actual location its value will be close to 1, if far
# away then the value will be smaller
##
def prob_estimate(particle, marker):
    m_x, m_y, m_h = parse_marker_info(marker[0], marker[1], marker[2])
    mu = np.matrix([[particle.x - m_x],\
                    [particle.y-m_y],\
                    [math.radians(diff_heading_deg(particle.h,m_h))]])
    matrixmath = mu.transpose()*sigma_inv*mu
    
    return math.e **-(matrixmath.item(0,0)/2)
