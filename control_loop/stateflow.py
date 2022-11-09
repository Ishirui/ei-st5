from perception import perception

## GLOBAL VARIABLES
v = 10


erreur_orientation = 0
detect_obs = 0
detect_inter = 0
detect_out = 0

def main():
    while True:
        
        image = 0 # Remplacer pour chopper feed camera

        erreur_orientation, detect_inter, detect_out = perception(image)

        new_state = curr_state.transition(detect_obs = detect_obs, detect_inter = detect_out, detect_inter = detect_inter)
        if new_state != curr_state:
            curr_state.exit()
        
            curr_state = new_state

            curr_state.entry()

        curr_state.during(v = v, erreur_orientation = erreur_orientation)


if __name__ == "__main__":
    main()
