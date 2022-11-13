from time import time
from math import sinh
from ..arduino_comm.transmit import v_max, K
import sys

class State:
    def __init__(self, bot):
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


class SuivreLigne(State):
    outer_gain = 3 ######################### Remplacer par le bon gain
    inner_gain = 2.3
    bias = 0.4

    def corrected_sinh(self, bot, x):
        sinh_correction = sinh(1)
        max_w = (1/K)*(v_max-bot.v)#The maximum w such that v+K*w doesn't exceed v_max ,as defined in arduino_comm.transmit
    
        x = x/bot.camera_resolution[0]

        if x > 1:
            x = 1

        if x < -1:
            x = -1

        return (max_w/sinh_correction)*sinh(x)

    def during(self, bot):
        w = self.outer_gain*self.corrected_sinh(self.inner_gain*bot.turn_error) + self.bias
        return (bot.target_v, w)