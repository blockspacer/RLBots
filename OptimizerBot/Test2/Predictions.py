  #imports for LQR functions
from __future__ import division, print_function

import multiprocessing as mp
import matplotlib.pyplot as plt
import math
import Plotting
from CoordinateSystems import CoordinateSystems
from BallController import BallController
from pyquaternion import Quaternion
from TrajectoryGeneration import Trajectory


from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState
from rlbot.utils.game_state_util import CarState
from rlbot.utils.game_state_util import Physics
from rlbot.utils.game_state_util import Vector3
from rlbot.utils.game_state_util import Rotator
from rlbot.utils.game_state_util import BallState

import random
import control #Control system python library
import numpy as np
#import slycot

#imports for LQR functions
# from __future__ import division, print_function
import numpy as np
import scipy.linalg


def predict(position, velocity, q, omega, a, torques, t0, t1):
    # print("p:", position, "v:", velocity, "q:", q, "omega:", omega, "a:", a, "torques:", torques)#, "t0:", t0, "t1:", t1)
    g = np.array([0,0,-650]) # Gravity
    dt = t1 - t0 # delta t
    v1 = (a + g)*dt + velocity # final velocity
    d1 = (a+g)*(np.power(dt, 2))
    p1 = ((d1) / 2) + (velocity*dt) + position

    return p1, v1

def predict_ball_to_ground(ball, tnow):
    s = ball.position
    v = ball.velocity
    # Define some constants
    g = np.array([0,0,-650]).transpose()
    ball_radius = 92.75 # uu

    # Solve the roots equation using the z elements of the vectors
    poly_z = np.array([-650/2, v[2], s[2] - ball_radius])
    time_to_ground = np.roots(poly_z)

    # Make sure time to ground is positive
    if(time_to_ground[0] < 0):
        t_ground = time_to_ground[1]
    elif(time_to_ground[1] < 0):
        t_ground = time_to_ground[0]

    #Use time_to_ground to get full position vector (make sure to use positive value)
    s_t = (g/2)*(t_ground**2) + (v * t_ground) + s

    # print('s_t', s_t, 'time to ground', t_ground)

    return time_to_ground[1], s_t

def predictBallTrajectory(ball, tnow):
    s = ball.position
    v = ball.velocity
    g = np.array([0,0,-650]).transpose()
    t = np.linspace(0, 20, num =20).transpose()
    vplus = (np.outer(g,t).transpose() + v).transpose()
    splus = ((np.outer(g, np.power(t,2)).transpose() / 2) + np.outer(v, t).transpose() + s).transpose()

    # print('s', s, 'splus', splus)
    return splus

def ballPredictionError(s_before, s_now, v_before, v_now, tbefore, tnow):
    g = np.array([0,0,-650])
    #is the excessive rendering causing timing issues?
    dt = tnow - tbefore #???????????is there some sort of timing issue with the function? is it behind or something?
    v_predict = g*dt + v_before
    s_predict = (g*(dt**2) / 2) + v_predict*dt + s_before
    square_error = (s_predict - s_now)**2
    # print('tnow', tnow, 'tbefore', tbefore)
    return square_error
