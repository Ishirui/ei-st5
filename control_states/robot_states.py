from time import time
from math import sinh
from arduino_comm.transmit import v_max, K
from grid_navigation.navigate_grid import generate_movements
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
        
        new_state = self.transition_conditions(bot)
        return new_state if new_state is not None else self

    def transition_conditions(self, bot):
        pass

class Init(State):
    #Wait for everything to be properly initialized
    def during(self, bot):
        return (0,0)

    def transition_conditions(self, bot):
        if not bot.detect_out and bot.obstacle_buffer == 0:
            return Acceleration()


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
        max_w = (1/K)*(v_max-bot.target_v)#The maximum w such that v+K*w doesn't exceed v_max ,as defined in arduino_comm.transmit
    
        x = x/bot.camera_resolution[0]

        if x > 1:
            x = 1

        if x < -1:
            x = -1

        return (max_w/sinh_correction)*sinh(x)

    def during(self, bot):
        w = self.outer_gain*self.activation_function(bot, self.inner_gain*bot.turn_error) + self.bias
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
class HandleIntersection(State): #Aussi appelé "virage"
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
        
        #Update histories
        if self.direction == "stop":
            bot.delivery_history.append(bot.curr_pos)
        elif self.direction in ["f","g","d","b"]:
            bot.turn_history.append(self.direction)

        pass
    
    def transition_conditions(self, bot):
        if time() - self.start_time > self.turn_params[self.direction][1]:
            if self.direction == "stop":
                self.direction = next(bot.instructions)

            if self.direction == "fin":
                return Stop()
            
            return Acceleration()
    
class Obstacle(State):
    wait_time = 0.1 #Time between braking and start recalculating
    
    def entry(self, bot):
        bot.obstacle_buffer = 0
    
    def during(self, bot):
        if time() - self.start_time > Freinage.brake_time:
            return (-bot.target_v, 0)
        else:
            return (0,0)

    def exit(self, bot):
        #We have to flip the start_cardinality, we could have handled that in generate_movements but eh
        new_heading = virage[bot.curr_heading]["g"]
        new_heading = virage[new_heading]["g"]

        next_node = (bot.curr_pos[0] + translation[bot.curr_heading][0], bot.curr_pos[1] + translation[bot.curr_heading][1])

        bot.aretes_cassees.append((bot.curr_pos, next_node))

        new_instructions, new_ordered_deliveries = generate_movements(bot.n, bot.curr_pos, bot.home_pos, new_heading)
        bot.instructions = (x for x in new_instructions)
        bot.deliveries_to_do_coords = new_ordered_deliveries

    def transition_conditions(self, bot):
        if time() - self.start_time > Freinage.brake_time + self.wait_time:
            return DemiTour()

class DemiTour(State):
    turn_time = 2*HandleIntersection.turn_90_time

    def during(self, bot):
        return (0, bot.target_w)

    def exit(self, bot):
        #Update history
        bot.turn_history.append("b")

    def transition_conditions(self, bot):
        if time() - self.start_time > self.turn_time:
            return SuivreLigne()

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