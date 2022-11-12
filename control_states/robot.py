from dataclasses import dataclass
from typing import Generator
from .robot_states import *

@dataclass
class Robot:
    # An object storing all parameters 


    # Dynamic parameters
    target_v = 0.3
    target_w = 1.5

    obst_detect_distance = 30
    obst_buff_size = 5

    camera_resolution = (160, 128)

    #Feature switches
    do_intersections = True
    do_obstacles = True
    do_road_exit = True

    road_exit_behavior = "u-turn" # "u-turn" or "stop"

    #Position and orientation states
    curr_state: State
    curr_pos: tuple
    curr_heading: str

    #Navigational state
    instructions: Generator[str]
    deliveries_to_do_coords: list

    turn_history = []
    delivery_history = []
    
    #Perception states
    detect_inter = False
    detect_out = False
    turn_error = 0.

    #Obstacle handling
    obstacle_buffer = 0