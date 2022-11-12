from control_loop.perception import perception
from control_loop.states import *
from comm_ard.envoi_commande_arduino import transmit
from algos_chemins.routes import deplacement_quadrillage, quadrillage
from comm_ard.obstacle import distance_capteur
import time

# GLOBAL VARIABLES
v = 0.3  # Vitesse de consigne, en m.s^-1 - doit être compris entre ~0.15 et 0.45
thresh_obs = 50  # Distance limite de detection d'obstacle en cm
detect_obs_thresh = 5  # Nb de hits qu'il faut avant de lancer un arrêt d'urgence
# Nb d'itérations qu'il faut pour valider une détection d'intersection rond point
thresh_roundabout = 10
nb_inter_roundabout = 0  # numéro de l'intersection détectée pour le rond point
i_roundabout = 0  # compteur pour la détection rond point


mode = "quad"  # "8" ou "quad" ou "roundabout" pour 8 ou quadrillage ou rond point
N = 4  # Nombre de noeuds sur le cote du quadrillage
point_depart = [0, 0]
livraisons = [[3, 3], [2, 2], [0, 3]]
pre_depart = [0, 1]
arretes_cassees = []
quadrillage = (N, point_depart, livraisons, pre_depart, arretes_cassees)
# [manoeuvre,position,liste_livraison_ordonnee]
# deplacement_quadrillage(n,point_depart,points_livraison,orientation,arretes_cassees)
# avancement dans la liste position -> il va vers position[avancement]
avancement = 0
erreur_orientation = 0
detect_obs_count = 0

detect_obs = False

detect_inter = 0
detect_out = 0

curr_state = SuivreLigne()

consigne = (0, 0)

if mode == "8":
    def generator():
        while True:
            yield "milieu"
    instructions = generator()
else:
    instruction_liste, positions, liste_livraison_ordonnee = deplacement_quadrillage(
        *quadrillage)
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
    global arretes_cassees

    while True:

        try:
            erreur_orientation, detect_inter, detect_out, missing = perception(
                False, mode)
            detect_obs = False

            # code de détection d'obstacle
            x = distance_capteur()
            if 0 < x <= thresh_obs:
                detect_obs_count += 1
            else:
                detect_obs_count = 0

            if detect_obs_count >= detect_obs_thresh:
                detect_obs = True
                detect_obs_count = 0

            # code de détection de rond point
            if missing == "Left" or missing == "Right":  # code de threshold pour éviter les faux positifs
                i_roundabout += 1
            else:
                i_roundabout = 0
            # si on détecte bien une intersection (COOLDOWN à AJOUTER/ threshold value?)
            if i_roundabout >= thresh_roundabout:
                nb_inter_roundabout += 1  # on la comptabilise
                i_roundabout = 0  # on reset la détection

        except Exception as e:
            print("Erreur de perception:"+str(e))
            erreur_orientation, detect_inter, detect_out = 0, 0, 0

        if mode == "8":  # TODO: Virer ça quand on sera sur l'environnement de test réel
            detect_inter = 0

        new_state = curr_state.transition(detect_obs=detect_obs, detect_out=detect_out,
                                          detect_inter=detect_inter, erreur_orientation=erreur_orientation, nb_inter_roundabout=nb_inter_roundabout, mode=mode, missing=missing)
        if new_state != curr_state:

            recalcul = curr_state.exit(
                mode=mode, arretes_cassees=arretes_cassees, avancement=avancement, positions=positions)
            if bool(recalcul):
                print('Recalcul en cours...')
                point_depart, pre_depart, arretes_cassees = recalcul
                quadrillage = (
                    N, point_depart, liste_livraison_ordonnee, pre_depart, arretes_cassees)
                instruction_liste, positions, liste_livraison_ordonnee = deplacement_quadrillage(
                    *quadrillage)
                instructions = (x for x in instruction_liste)
                print('Nouvelles instructions : ', instruction_liste)

            curr_state = new_state

            if curr_state.entry(v=v, instructions=instructions, liste_livraison_ordonnee=liste_livraison_ordonnee, mode=mode, nb_inter_roundabout=nb_inter_roundabout, missing=missing):
                # entry renvoit True uniquement lorsque le nouvel etat est une intersection
                avancement = avancement + 1

            print(curr_state)

        consigne = curr_state.during(
            v=v, erreur_orientation=erreur_orientation)

        if consigne is None:
            consigne = (0, 0)

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
        consigne = (0, 0)
        start = time.time()
        failsafe(start)
