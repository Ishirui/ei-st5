from control_loop.perception import perception
from control_loop.states import *
from comm_ard.envoi_commande_arduino import transmit
from algos_chemins.routes import deplacement_quadrillage, quadrillage
from comm_ard.obstacle import distance_capteur
import time

## GLOBAL VARIABLES
v = 0.3 # Vitesse de consigne, en m.s^-1 - doit être compris entre ~0.15 et 0.45
thresh_obs = 50 # Distance limite de detection d'obstacle en cm
detect_obs_thresh = 5 #Nb de hits qu'il faut avant de lancer un arrêt d'urgence

<<<<<<< HEAD
mode = "8" # "8" ou "quad" pour 8 ou quadrillage
quadrillage = (4, [0,0], [[3,3], [2,2], [0,3]], [0,1], [])
=======
>>>>>>> 4859f8f052dbfd76a19693bfde5a5c9aa3e50135

mode = "quad" # "8" ou "quad" pour 8 ou quadrillage
N = 4 # Nombre de noeuds sur le cote du quadrillage
point_depart = [0,0]
livraisons = [[3,3], [2,2], [0,3]]
pre_depart = [0,1]
arretes_cassees = []
quadrillage = (N, point_depart, livraisons, pre_depart, arretes_cassees)
#[manoeuvre,position,liste_livraison_ordonnee]
#deplacement_quadrillage(n,point_depart,points_livraison,orientation,arretes_cassees)
avancement = 0 # avancement dans la liste position -> il va vers position[avancement]
erreur_orientation = 0
detect_obs_count = 0

detect_obs = False

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
    instruction_liste,positions,liste_livraison_ordonnee = deplacement_quadrillage(*quadrillage)
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
            print("Erreur de perception:"+str(e))
            erreur_orientation, detect_inter, detect_out = 0,0,0

        if mode == "8": #TODO: Virer ça quand on sera sur l'environnement de test réel
            detect_inter = 0


        new_state = curr_state.transition(detect_obs = detect_obs, detect_out = detect_out, detect_inter = detect_inter, erreur_orientation = erreur_orientation)
        if new_state != curr_state:
        

            recalcul = curr_state.exit(mode = mode, arretes_cassees = arretes_cassees, avancement = avancement, positions = positions)
            if bool(recalcul):
                print('Recalcul en cours...')
                point_depart, pre_depart, arretes_cassees = recalcul
                quadrillage = (N, point_depart, liste_livraison_ordonnee, pre_depart, arretes_cassees)
                instruction_liste, positions, liste_livraison_ordonnee = deplacement_quadrillage(*quadrillage)
                instructions = (x for x in instruction_liste)
                print('Nouvelles instructions : ', instruction_liste)
    
            curr_state = new_state

            if curr_state.entry(v = v, instructions = instructions, liste_livraison_ordonnee = liste_livraison_ordonnee):
                avancement = avancement + 1 # entry renvoit True uniquement lorsque le nouvel etat est une intersection

            print(curr_state)

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
    finally:
        print("Exiting...")
        consigne = (0,0)
        start = time.time()
        failsafe(start)


