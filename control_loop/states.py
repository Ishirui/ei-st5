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

    def during(self, **kwargs):
        v = kwargs['v']
        erreur_orientation = kwargs['erreur_orientation']

        w = 0.5 * erreur_orientation
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

    def __init__(self):
        start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,0)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > 2:
            return DemiTour()

class DemiTour(BaseState):

    def __init__(self):
        start_time = time.time()
    
    def during(self, **kwargs):
        consigne = (0,0.8)
        return consigne

    def transition_conditions(self, *args, **kwargs):
        if time.time() - self.start_time > 4:
            return SuivreLigne()



        
        