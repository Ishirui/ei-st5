from control_loop.perception import perception
from control_loop.states import *
from comm_ard.envoi_commande_arduino import transmit
from algos_chemins.routes import deplacement_quadrillage, quadrillage
from comm_ard.obstacle import distance_capteur

## GLOBAL VARIABLES
v = 0.2 # Vitesse de consigne, en m.s^-1 - doit être compris entre ~0.15 et 0.45
thresh_obs = 20 # Distance limite de detection d'obstacle en cm

mode = "8" # "8" ou "quad" pour 8 ou quadrillage
quadrillage = (4, [0,0], [[3,3], [2,2], [0,3]], [0,1])

erreur_orientation = 0
detect_obs = 0
detect_inter = 0
detect_out = 0

curr_state = SuivreLigne()

consigne = (0,0)

if mode == "8":
    def generator():
        while True:
            yield "milieu"
    instructions = generator()
else:
    instructions = (x for x in deplacement_quadrillage(*quadrillage))
    print(deplacement_quadrillage(*quadrillage))



def main():
    global curr_state
    global consigne
    global instructions
    global detect_obs
    global erreur_orientation
    global detect_inter
    global detect_out
    while True:

        try:
            erreur_orientation, detect_inter, detect_out = perception()
            detect_obs = bool(distance_capteur() <= thresh_obs)
        except Exception as e:
            print("Erreur de perception:"+str(e))
            erreur_orientation, detect_inter, detect_out = 0,0,0

        detect_inter = 0

        new_state = curr_state.transition(detect_obs = detect_obs, detect_out = detect_out, detect_inter = detect_inter)
        if new_state != curr_state:
        

            new_instr = curr_state.exit()
            if new_instr:
                instructions = new_instr
        
            curr_state = new_state

            curr_state.entry(v=v, instructions = instructions)

            print(curr_state)

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
        time.sleep(1)
