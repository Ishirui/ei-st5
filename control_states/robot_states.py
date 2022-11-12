from time import time
import sys

class State:
    def __init__(self, robot, **kwargs):
        self.start_time = time()

    def entry(self, robot, **kwargs):
        values = {}
        return values

    def during(self, robot, **kwargs):
        order = (0,0)
        return order

    def exit(self, robot, **kwargs):
        values = {}
        return values

    def transition(self, robot, **kwargs):
        stop = kwargs["stop"]
        if stop:
            return Stop()
        
        new_state = self.transition_conditions(self, robot, **kwargs)
        return new_state if new_state is not None else self

    def transition_conditions(self, robot, **kwargs):
        pass


class Stop(State):
    brake_time = 0.1
    time_before_exit = 0.5

    def during(self, robot, **kwargs):
        if self.time_before_exit > time() - self.start_time > self.brake_time:
            return (0,0)
        else:
            return (-robot.target_v,0)
        
    def exit(self, robot, **kwargs):
        print("Done !")
        sys.exit(0)

