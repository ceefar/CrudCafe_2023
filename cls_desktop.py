# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----


# ---- Imports ----
import pygame as pg

# ---- Internal Imports ----
from cls_state_machine import StateMachine
from settings import *


# ---- Desktop : Parent Class ----

class Desktop(pg.sprite.Sprite):
    def __init__(self, game):
        # -- core setup --
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # -- setup state machine, starts in default idle state --
        self.state_machine = StateMachine(DesktopStateIdle(self)) 
        # -- setup default rect and image --
        self.image = pg.Surface((WIDTH, HEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        
    def update(self):
        self.state_machine.update()

    def draw(self, screen):
        self.state_machine.draw(screen)

    def handle_events(self, event):
        self.state_machine.handle_events(event)

# ---- State ----
class DesktopState:
    def __init__(self, desktop:Desktop):
        self.desktop = desktop
        self.game = desktop.game
        self.bg_colour = WIN95GREEN
     
    # ---- Events, Draw, and Update Things ----
    def handle_events(self, event):
        ...

    def draw(self, screen:pg.Surface):
        screen.blit(self.desktop.image, self.desktop.rect)

    def update(self):
        self.desktop.image.fill(self.bg_colour)

    def change_state_to_desktop_1_idle(self):
        self.desktop.state_machine.change_state(DesktopStateIdle(self.desktop))

    def change_state_to_desktop_2_info(self):
        self.desktop.state_machine.change_state(DesktopStateInfo(self.desktop))

    def change_state_to_desktop_3_orders_menu(self):
        self.desktop.state_machine.change_state(DesktopStateOrdersMenu(self.desktop))


# ---- Desktop - 1.Idle : Child State ----
class DesktopStateIdle(DesktopState):
    def __init__(self, desktop:Desktop):
        super().__init__(desktop)
        self.bg_colour = WHITE

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_2:
                self.change_state_to_desktop_2_info()
            if event.key == pg.K_3:
                self.change_state_to_desktop_3_orders_menu()


# ---- Desktop - 2.Info : Child State ----
class DesktopStateInfo(DesktopState):
    def __init__(self, desktop:Desktop):
        super().__init__(desktop)
        self.bg_colour = RED

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                self.change_state_to_desktop_1_idle()
            if event.key == pg.K_3:
                self.change_state_to_desktop_3_orders_menu()


# ---- Desktop - 3.Orders Menu : Child State ----
class DesktopStateOrdersMenu(DesktopState):
    def __init__(self, desktop:Desktop):
        super().__init__(desktop)
        self.bg_colour = YELLOW

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                self.change_state_to_desktop_1_idle()
            if event.key == pg.K_2:
                self.change_state_to_desktop_2_info()
      

