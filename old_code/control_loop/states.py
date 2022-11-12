import time
from sys import exit
from math import sinh

virage = {'n': {'g':'w', 'd':'e', 'f':'n', 'b':'s', 'stop':'n'},\
          's': {'g':'e', 'd':'w', 'f':'s', 'b':'n', 'stop':'s'},\
          'e': {'g':'n', 'd':'s', 'f':'e', 'b':'w', 'stop':'e'},\
          'w': {'g':'s', 'd':'n', 'f':'w', 'b':'e', 'stop':'w'}}

last_inter_time = 0

class BaseState:
    def __init__(self, **kwargs):
        pass

    def entry(self, **kwargs):
        pass

    def during(self, **kwargs):
        pass

    def exit(self, **kwargs):
        pass

    def transition(self, *args, **kwargs):
        new_state = self.transition_conditions(self, *args, **kwargs)
        return new_state if new_state is not None else self

    def transition_conditions(self, *args, **kwargs):
        pass


class SuivreLigne(BaseState):
    outer_correction_gain = 3 ######################### Remplacer par le bon gain
    inner_correction_gain = 2.3
    intersection_cooldown_time = 2
    static_gain = 0.4
    
    def during(self, **kwargs):
        v = kwargs['v']
        erreur_orientation = kwargs['erreur_orientation']

        w = self.outer_correction_gain * sinh((self.inner_correction_gain*v/0.2)/self.outer_correction_gain*erreur_orientation/160) + self.static_gain
        consigne = (v,w)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_obs = kwargs['detect_obs']
        detect_inter = kwargs['detect_inter']
        detect_out = kwargs['detect_out']
        
        if detect_obs == 1:
            return ArretUrgence()
        elif detect_inter == 1 and time.time() - last_inter_time > 2:
            return Intersection()
        elif detect_out == 1:
            return SortieRoute()


class ArretUrgence(BaseState):
    stop_time = 2

    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def entry(self, **kwargs):
        pass

    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def exit(self, **kwargs):
        positions = kwargs['positions']
        aretes_cassees = kwargs['aretes_cassees']
        avancement = kwargs['avancement']
        mode = kwargs['mode']

        if mode == 'quad':
            point_depart = positions[avancement-1]
            pre_depart = positions[avancement]
            aretes_cassees.append((pre_depart,point_depart))
            return (point_depart, aretes_cassees)

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.stop_time:
            return DemiTour()


class DemiTour(BaseState):
    turn_time = 2
    turn_w = 1.7

    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,self.turn_w)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.turn_time:
            return SuivreLigne()


class Intersection(BaseState):
    # center_time = 0.3 #################### A calibrer
    center_time = 0.4
    cooldown_time = 2


    def __init__(self, **kwargs):
        self.start_time = time.time()

    def entry(self, **kwargs):

        # Delai min entre 2 intersection
        global last_inter_time
        last_inter_time = self.start_time
        v = kwargs["v"]
        self.center_time = self.center_time*0.2/v

        return True


    def during(self, **kwargs):
        v = kwargs['v']
        consigne = (v,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_inter = kwargs['detect_inter']
        if not detect_inter:
            if time.time() - self.start_time > self.center_time:
                return ChoixDirection()
        else:
            self.start_time = time.time()
        

class ChoixDirection(BaseState):
    turn_w = 1.6
    turn_time = 1.2
    deliver_time = 1.5

    def __init__(self, **kwargs):
        self.start_time = time.time()

    def entry(self, **kwargs):
        instructions = kwargs['instructions']
        liste_livraison_ordonnee = kwargs['liste_livraison_ordonnee']

        self.frein_count = 2

        v = kwargs["v"]
        try:
            self.direction = next(instructions)
        except StopIteration:
            print("Fin du chemin !")
            self.direction = "FIN"

        if self.direction == 'g':
            self.consigne = (0,self.turn_w) 
        elif self.direction == 'd':
            self.consigne = (0,-self.turn_w) ################## Potentiellement, changer de signes
        elif self.direction == 'f':
            self.frein_count = 0
            self.consigne = (v, 0)
        elif self.direction == "b":
            self.turn_time = 2*self.turn_time
            self.consigne = (0,self.turn_w)
        elif self.direction == "stop":
            self.consigne = (0,0)
            if len(liste_livraison_ordonnee) > 0:
                liste_livraison_ordonnee.pop(0)
        else:
            self.consigne = (0,0)

    def during(self, **kwargs):
        v = kwargs["v"]
        
        if self.frein_count > 0:
            self.frein_count -= 1
            return (-v,0)

        return self.consigne

    def exit(self, **kwargs):
        curr_card = kwargs['curr_card']
        return virage[curr_card][self.direction]

    def transition_conditions(self, *args, **kwargs):
        
        if self.direction == "FIN":
            return Stop()
        
        if self.direction == "f":
            return SuivreLigne()

        if self.direction == "stop":
            if time.time() - self.start_time > self.deliver_time:
                return ChoixDirection()
        else:
            if time.time() - self.start_time > self.turn_time:
                return SuivreLigne()


class SortieRoute(BaseState):
    try_rejoin_time = 2

    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_out = kwargs['detect_out']


        if detect_out == 0:
            return SuivreLigne()
        if time.time() - self.start_time > self.try_rejoin_time:
            return ChercheRoute()
            return DemiTourSR()


class DemiTourSR(BaseState):
    turn_time_SR = 1.5
    turn_w_SR = 1.7

    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,self.turn_w_SR)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.turn_time_SR:
            return ChercheRoute()


class ChercheRoute(BaseState):

    def during(self, **kwargs):
        v = kwargs['v']

        consigne = (-v/2,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_out = kwargs['detect_out']
        
        if detect_out == 0:
            return SuivreLigne()

class Stop(BaseState):
    stop_time = 1
    
    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.stop_time:
            exit(0)
            