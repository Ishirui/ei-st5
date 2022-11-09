import time


class BaseState:
    def __init__():
        pass

    def entry(self):
        pass

    def during(self):
        pass

    def exit(self):
        pass

    def transition(self, *args, **kwargs):
        new_state = self.transition_conditions(self, *args, **kwargs)
        return new_state if new_state is not None else self

    def transition_conditions(self, *args, **kwargs):
        pass


class SuivreLigne(BaseState):
    line_correction_gain = 0.5 ######################### Remplacer 0.5 par le bon gain
    
    def during(self, **kwargs):
        v = kwargs['v']
        erreur_orientation = kwargs['erreur_orientation']

        w = self.line_correction_gain * erreur_orientation
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

    def __init__(self):
        start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.stop_time:
            return DemiTour()


class DemiTour(BaseState):
    turn_time = 4
    turn_w = 0.8

    def __init__(self):
        start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,self.turn_w)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > self.turn_time:
            return SuivreLigne()


class Intersection(BaseState):

    def __init__(self):
        start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > 2:
            return ChoixDirection()
        

class ChoixDirection(BaseState):
    turn_w = 2 ############################ Remplacer 2 par bonne constante

    def __init__(self, **kwargs):
        instructions = kwargs['instructions']
        direction = instructions.pop() ################## A voir si on garde pop

    def during(self, **kwargs):
        v = kwargs['v']
        
        if self.direction == 'G':
            consigne = (v,self.turn_w) 
        if self.direction == 'D':
            consigne = (v,-self.turn_w) ################## Potentiellement, changer de signes
        else:
            consigne = (v,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        detect_inter = kwargs['detect_inter']
        
        if detect_inter == 0:
            return SuivreLigne()


class SortieRoute(BaseState):
    try_rejoin_time = 1


    def __init__(self):
        start_time = time.time()
    
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
    turn_time_SR = 4
    turn_w_SR = 0.8


    def __init__(self):
        start_time = time.time()
    
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