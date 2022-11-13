from .robot_states import *
from ..image_processing.perception import perception, resolution_target
from ..arduino_comm.obstacle import distance_capteur

class Robot:
    # An object storing all parameters 

    # Dynamic parameters
    target_v = 0.3
    target_w = 0.45

    obst_detect_distance = 30
    obst_buff_size = 5

    camera_resolution = resolution_target

    n = 4
    home_pos = (0,0)

    #Feature switches
    do_intersections = True
    do_obstacles = True
    do_road_exit = True

    road_exit_behavior = "u-turn" # "u-turn" or "stop"

    #Position and orientation states
    curr_state = None
    curr_pos = None
    curr_heading = None

    #Navigational state
    instructions = None
    deliveries_to_do_coords = []
    stop = False

    broken_edges = []
    turn_history = []
    delivery_history = []
    
    #Perception states
    detect_inter = False
    detect_out = False
    turn_error = 0.

    #Obstacle handling
    obstacle_buffer = 0

    def __init__(self, **kwargs):
        for el in dir(self):
            if el in kwargs:
                setattr(self, el, kwargs[el])


    def do_perception(self):
        self.turn_error, self.detect_inter, self.detect_out = perception()
        dist_obst = distance_capteur()
        if dist_obst <= self.obst_detect_distance:
            self.obstacle_buffer += 1

