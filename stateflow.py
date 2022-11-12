from control_loop.perception import perception
from control_loop.states import *
from comm_ard.envoi_commande_arduino import transmit
from algos_chemins.algo_chemins import generate_movements
from comm_ard.obstacle import distance_capteur
import time
import traceback

## GLOBAL VARIABLES
v = 0.5 # Vitesse de consigne, en m.s^-1 - doit être compris entre ~0.15 et 0.45
thresh_obs = 30 # Distance limite de detection d'obstacle en cm
detect_obs_thresh = 5 #Nb de hits qu'il faut avant de lancer un arrêt d'urgence

mode = "quad" # "8" ou "quad" pour 8 ou quadrillage
N = 4 # Nombre de noeuds sur le cote du quadrillage
#point_depart_abs = (0,0)
point_depart = (0,0)
point_fin = point_depart
livraisons = [(2,2), (0,3)]
curr_card = 'n'
aretes_cassees = []
#[manoeuvre,position,liste_livraison_ordonnee]
#generate_movements(n,point_depart,points_livraison,orientation,aretes_cassees)
avancement = 0 # avancement dans la liste position -> il va vers position[avancement]
erreur_orientation = 0
detect_obs_count = 0

detect_obs = False

detect_inter = 0
detect_out = 0

curr_state = SuivreLigne()

consigne = (0,0)
instruction_liste, positions, liste_livraison_ordonnee = [], [], []


if mode == "8":
    def generator():
        while True:
            yield "milieu"
    instructions = generator()
else:
    instruction_liste, positions,liste_livraison_ordonnee = generate_movements(N, point_depart, point_fin, curr_card, livraisons, aretes_cassees)
    instructions = (x for x in instruction_liste)
    print(instruction_liste)



def main():
    global curr_state
    global consigne
    global instructions
    global detect_obs
    global erreur_orientation
    global detect_inter
    global detect_out
    global detect_obs_count
    global avancement
    global liste_livraison_ordonnee
    global positions
    global aretes_cassees
    global curr_card

    while True:

        try:
            erreur_orientation, detect_inter, detect_out = perception()
            detect_obs = False
            x = distance_capteur()
            if 0 < x <= thresh_obs:
                detect_obs_count += 1
            else:
                detect_obs_count = 0
                

            if detect_obs_count >= detect_obs_thresh :
                detect_obs = True
                detect_obs_count = 0
        except Exception as e:
            print("Erreur de perception:" + str(e))
            erreur_orientation, detect_inter, detect_out = 0, 0, 0

        if mode == "8": #TODO: Virer ça quand on sera sur l'environnement de test réel
            detect_inter = 0


        new_state = curr_state.transition(detect_obs = detect_obs, detect_out = detect_out, detect_inter = detect_inter, erreur_orientation = erreur_orientation)
        if new_state != curr_state:
        

            exit_res = curr_state.exit(mode = mode, aretes_cassees = aretes_cassees, avancement = avancement, positions = positions, curr_card = curr_card)

            if type(exit_res) == str:
                curr_card = exit_res
            elif exit_res:
                print('Recalcul en cours...')
                point_depart, aretes_cassees = exit_res
                curr_card = virage[curr_card]['b']
                instruction_liste, positions, liste_livraison_ordonnee = generate_movements(N, point_depart, curr_card, liste_livraison_ordonnee, aretes_cassees)
                instructions = (x for x in instruction_liste)
                print('Nouvelles instructions : ', instruction_liste)
    
            curr_state = new_state

            if curr_state.entry(v = v, instructions = instructions, liste_livraison_ordonnee = liste_livraison_ordonnee):
                avancement = avancement + 1 # entry renvoit True uniquement lorsque le nouvel etat est une intersection

            print(curr_state)
            print(liste_livraison_ordonnee)

        consigne = curr_state.during(v = v, erreur_orientation = erreur_orientation)

        if consigne is None:
            consigne = (0,0)

        transmit(*consigne)

def failsafe(start):
    try:
        while time.time() - start < 1:
            transmit(*consigne)
        return
    except:
        failsafe(start)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
    finally:
        print("Exiting...")
        consigne = (0,0)
        start = time.time()
        failsafe(start)


