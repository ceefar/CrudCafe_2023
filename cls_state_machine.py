# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----


# ---- State Machine Parent Class ----
class StateMachine:
    """ generalised state machine so can be used for different types of objects """
    def __init__(self, initial_state):
        self.current_state = initial_state

    def change_state(self, new_state):
        self.current_state = new_state

    def handle_events(self, event):
        self.current_state.handle_events(event)

    def update(self):
        self.current_state.update()

    def draw(self, screen):
        self.current_state.draw(screen)
