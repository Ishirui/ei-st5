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
        newState = self
        return newState

class SuivreLigne(BaseState):
    def entry():
        pass



def main():
    while True:
        new_state = curr_state.transition()
        if new_state != curr_state:
            curr_state.exit()
        
            curr_state = new_state

            curr_state.entry()

        curr_state.during()


if __name__ == "__main__":
    main()
