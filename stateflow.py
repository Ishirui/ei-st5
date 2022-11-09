from control_loop.perception import perception
from control_loop.states import *
from comm_ard.envoi_commande_arduino import transmit

## GLOBAL VARIABLES
v = 0.2 #Vitesse de consigne, en m.s^-1 - doit être compris entre ~0.15 et 0.45

erreur_orientation = 0
detect_obs = 0
detect_inter = 0
detect_out = 0

curr_state = SuivreLigne()

consigne = (0,0)

def generator():
    while True:
        yield "F"

instructions = generator() ################## A mieux initialiser

def main():
    global curr_state
    global consigne
    global instructions
    while True:

        try:
            erreur_orientation, detect_inter, detect_out = perception()
        except Exception as e:
            print("Erreur de perception:"+str(e))
            erreur_orientation, detect_inter, detect_out = 0,0,0


        new_state = curr_state.transition(detect_obs = detect_obs, detect_out = detect_out, detect_inter = detect_inter)
        if new_state != curr_state:
            
            new_instr = curr_state.exit()
            if new_instr:
                instructions = new_instr
        
            curr_state = new_state

            curr_state.entry(instructions = instructions)

        consigne = curr_state.during(v = v, erreur_orientation = erreur_orientation)

        if consigne is None:
            consigne = (0,0)

        transmit(*consigne)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        consigne = (0,0)
        transmit(*consigne)
