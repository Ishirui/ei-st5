from control_states.robot import Robot
from control_states.robot_states import *
from arduino_comm.transmit import transmit
from traceback import print_exc

bot = Robot(\
    curr_state = SuivreLigne(),\
    curr_pos = None,\
    curr_heading = None,\
    delivery_to_do_coords = None
    )

bot.do_intersections = False

def main():
    
    old_state = bot.curr_state
    bot.do_perception()

    state = old_state.transition()
    if state != old_state:
        old_state.exit(bot)
        state.entry(bot)

        bot.curr_state = state
        print(f"Transition à t = {state.start_time} : {old_state} -> {state}")

    consigne = state.during(bot)

    transmit(consigne)

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Manual stop !")
            bot.stop = True
        except Exception as e:
            print_exc()
            bot.stop = True
        