from perception import perception
from states import *

## GLOBAL VARIABLES
v = 10

erreur_orientation = 0
detect_obs = 0
detect_inter = 0
detect_out = 0

curr_state = SuivreLigne()

def generator():
    while True:
        yield "F"


instructions = generator() ################## A mieux initialiser

def main():
    global curr_state
    while True:

        erreur_orientation, detect_inter, detect_out = perception()

        new_state = curr_state.transition(detect_obs = detect_obs, detect_out = detect_out, detect_inter = detect_inter)
        if new_state != curr_state:
            curr_state.exit()
        
            curr_state = new_state

            curr_state.entry(instructions = instructions)

        curr_state.during(v = v, erreur_orientation = erreur_orientation)

        # transmit(v,w)

if __name__ == "__main__":
    main()
