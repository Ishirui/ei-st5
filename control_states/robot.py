from .robot_states import *
from image_processing.perception import perception, resolution_target
from arduino_comm.obstacle import distance_capteur

class Robot:
    # An object storing all parameters 

    # Dynamic parameters
    target_v = 0.3
    target_w = 2

    obst_detect_distance = 25
    obst_buff_size = 5

    camera_resolution = resolution_target

    n = 5
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

    last_intersection_time = -1

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

        if self.deliveries_to_do_coords != []:


            if self.curr_pos[0] < 0 or self.curr_pos[1] < 0:
                start_pos = (self.curr_pos[0] + translation[self.curr_heading][0], self.curr_pos[1] + translation[self.curr_heading][1])
            else:
                start_pos = self.curr_pos


            new_instructions, new_ordered_deliveries = generate_movements(self.n, start_pos, self.home_pos, self.curr_heading, self.deliveries_to_do_coords, self.broken_edges)
            print(new_instructions)
            self.instructions = (x for x in new_instructions)
            self.deliveries_to_do_coords = new_ordered_deliveries


    def do_perception(self):
        self.turn_error, self.detect_inter, self.detect_out = perception()
        dist_obst = distance_capteur()
        if 0 < dist_obst <= self.obst_detect_distance:
            self.obstacle_buffer += 1
        else:
            self.obstacle_buffer = 0

