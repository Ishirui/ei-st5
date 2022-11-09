import time

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
    line_correction_gain = 10 ######################### Remplacer par le bon gain
    
    def during(self, **kwargs):
        v = kwargs['v']
        erreur_orientation = kwargs['erreur_orientation']

        w = self.line_correction_gain * erreur_orientation/320
        consigne = (v,w)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_obs = kwargs['detect_obs']
        detect_inter = kwargs['detect_inter']
        detect_out = kwargs['detect_out']
        
        if detect_obs == 1:
            return ArretUrgence()
        elif detect_inter == 1:
            return Intersection()
        elif detect_out == 1:
            return SortieRoute()


class ArretUrgence(BaseState):
    stop_time = 2

    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def entry(self, **kwargs):
        # Ajouter l'obstacle / update les poids de la map
        pass

    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def exit(self, **kwargs):
        # Recalculer l'itineraire
        pass

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.stop_time:
            return DemiTour()


class DemiTour(BaseState):
    turn_time = 2
    turn_w = 1.6

    def __init__(self, **kwargs):
        self.start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,self.turn_w)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.turn_time:
            return SuivreLigne()


class Intersection(BaseState):
    center_time = 0.5 #################### A calibrer

    def __init__(self, **kwargs):
        self.start_time = time.time()

    def during(self, **kwargs):
        v = kwargs['v']
        consigne = (v,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.center_time:
            return ChoixDirection()
        

class ChoixDirection(BaseState):
    turn_w = 1.6
    turn_time = 1

    def __init__(self, **kwargs):
        self.start_time = time.time()

    def entry(self, **kwargs):
        instructions = kwargs['instructions']
        self.direction = next(instructions)

    def during(self, **kwargs):

        if self.direction == 'G':
            consigne = (0,self.turn_w) 
        if self.direction == 'D':
            consigne = (0,-self.turn_w) ################## Potentiellement, changer de signes
        else:
            consigne = (0,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
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
            return DemiTourSR()


class DemiTourSR(BaseState):
    turn_time_SR = 2
    turn_w_SR = 1.6

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

        consigne = (v,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_out = kwargs['detect_out']
        
        if detect_out == 0:
            return SuivreLigne()