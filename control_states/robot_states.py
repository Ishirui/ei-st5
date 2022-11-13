from time import time
from math import sinh
from ..arduino_comm.transmit import v_max, K
import sys

virage = {'n': {'g':'w', 'd':'e', 'f':'n', 'b':'s', 'stop':'n', 'fin':'n'},\
          's': {'g':'e', 'd':'w', 'f':'s', 'b':'n', 'stop':'s', 'fin':'s'},\
          'e': {'g':'n', 'd':'s', 'f':'e', 'b':'w', 'stop':'e', 'fin':'e'},\
          'w': {'g':'s', 'd':'n', 'f':'w', 'b':'e', 'stop':'w', 'fin':'w'}}

translation = {'n':(0,1), 's':(0,-1), 'w':(-1,0), 'e':(0,1)}
class State:
    def __init__(self):
        self.start_time = time()

    def __repr__(self):
        return self.__class__.__name__

    def entry(self, bot):
        pass #Update the robot object

    def during(self, bot):
        order = (0,0)
        return order

    def exit(self, bot):
        pass #Update the robot object

    def transition(self, bot):
        if bot.stop:
            return Stop()
        
        new_state = self.transition_conditions(self, bot, )
        return new_state if new_state is not None else self

    def transition_conditions(self, bot):
        pass

class Acceleration(State):
    accel_time = 0.1

    def during(self, bot):
        return (100, 0) #Saturate the motors
    
    def transition_conditions(self, bot):
        if time() - self.start_time > self.accel_time:
            return SuivreLigne()
class SuivreLigne(State):
    outer_gain = 3 ######################### Remplacer par le bon gain
    inner_gain = 2.3
    bias = 0.4

    def activation_function(self, bot, x):
        sinh_correction = sinh(1)
        max_w = (1/K)*(v_max-bot.v)#The maximum w such that v+K*w doesn't exceed v_max ,as defined in arduino_comm.transmit
    
        x = x/bot.camera_resolution[0]

        if x > 1:
            x = 1

        if x < -1:
            x = -1

        return (max_w/sinh_correction)*sinh(x)

    def during(self, bot):
        w = self.outer_gain*self.activation_function(self.inner_gain*bot.turn_error) + self.bias
        return (bot.target_v, w)

    def transition_conditions(self, bot):
        if bot.do_road_exit and bot.detect_out:
            return RoadExit()
        
        if bot.do_obstacles and bot.obstacle_buffer >= bot.obst_buff_size:
            return Obstacle()

        if bot.do_intersections and bot.detect_inter:
            return ApprocheIntersection()   
class ApprocheIntersection(State):
    coast_time = 0.4
    
    def entry(self, bot):
        self.direction = next(bot.instructions)

    def during(self,bot):
        if bot.detect_inter == 0 and not self.coast:
            self.coast = True
            self.coast_start = time()
        
        return (bot.target_v, 0)

    def exit(self, bot):
        # Update bot's position on the grid
        bot.curr_pos = (bot.curr_pos[0] + translation[bot.curr_heading][0], bot.curr_pos[1] + translation[bot.curr_heading][1])

    def transition_conditions(self, bot):
        if self.coast and time() - self.coast_start > self.coast_time:
            if self.direction == "f":
                return SuivreLigne()
            else:
                return Freinage(self.direction)  
class Freinage(State):
    brake_time = 0.1
    
    def __init__(self, direction):
        super().__init__()
        self.direction = direction

    def during(self, bot):
        return (-bot.target_v, 0)
    
    def transition_conditions(self, bot):
        if time() - self.start_time > self.brake_time:
            return HandleIntersection(self.direction)
class HandleIntersection(State):
    turn_90_time = 1
    deliver_time = 1
    turn_params = {"f":(0,0), "g":(1, turn_90_time), "d":(-1, turn_90_time), "b":(-1, 2*turn_90_time), "stop":(0,deliver_time), "fin":(0,0)}

    def __init__(self, direction):
        super().__init__()
        self.direction = direction
    
    def entry(self, bot):
        if self.direction == "fin":
            print("Finished !")
            bot.stop = True

    def during(self, bot):
        return (0,bot.target_w*self.turn_params[self.direction][0])

    def exit(self, bot):
        #Update bot's heading
        bot.curr_heading = virage[bot.curr_heading][self.direction]
        pass
    
    def transition_conditions(self, bot):
        if time() - self.start_time > self.turn_params[self.direction][1]:
            if self.direction == "stop":
                self.direction = next(bot.instructions)

            if self.direction == "fin":
                return Stop()
            
            return Acceleration()

    
class Obstacle(State):
    def entry(self, bot):
        bot.obstacle_buffer = 0

    

class RoadExit(State):
    pass

class Stop(State):
    brake_time = 0.1
    time_before_exit = 0.5

    def during(self, bot):
        if self.time_before_exit > time() - self.start_time > self.brake_time:
            return (0,0)
        else:
            return (-bot.target_v,0)
        
    def exit(self, bot):
        print("Done !")
        sys.exit(0)