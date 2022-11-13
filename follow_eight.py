from numpy import False_
from control_states.robot import Robot
from control_states.robot_states import *
from arduino_comm.transmit import transmit
from traceback import print_exc
from sys import exit

start_time = time()

bot = Robot(\
    curr_state = Init(),\
    do_intersections = False,
    do_road_exit = False,
    do_obstacles = True
    )


def main():
    
    old_state = bot.curr_state
    bot.do_perception()

    state = old_state.transition(bot)
    if state != old_state:
        old_state.exit(bot)
        state.entry(bot)

        bot.curr_state = state
        print("Transition à t = {} : {} -> {}".format(state.start_time-start_time, old_state, state))

    consigne = state.during(bot)

    transmit(consigne)

if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("Manual stop !")
        bot.stop = True
    except Exception as e:
        print_exc()
        bot.stop = True
        transmit((0,0))
        exit(0)