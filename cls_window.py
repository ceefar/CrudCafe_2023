# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----

# ---- Imports ----
import pygame as pg
from random import choice

# ---- Internal Imports ----
from cls_state_machine import StateMachine
from settings import *

# ---- Consts - Move To Settings When Finalised ----
WIN_IDLE_SIZE = (0, 0)
WIN_SHELVED_SIZE = (100, 40)
WIN_OPENED_SIZE = (400, 400)


# -------- Window Classes --------
class Window(pg.sprite.Sprite):
    def __init__(self, game):
        # -- core setup --
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game


# todo >> ig for this pass it some info and just have it display that info...(maybe do that in update tbf duh!)
class InfoWindow(Window):
    def __init__(self, game):
        super().__init__(game)
        # -- setup instance vars --
        self.image = pg.Surface(WIN_OPENED_SIZE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        # -- log instantiation --
        print(f"\n- New Window [Info] Instance Created\n{'':2}- {self}")


class CustomerWindow(Window):
    def __init__(self, game, customer):
        super().__init__(game)
        self.my_customer = customer
        # -- setup state machine, starts in default idle state --
        self.state_machine = StateMachine(WindowStateIdle(self)) 
        # -- define core instance vars --
        self.image = pg.Surface(WIN_IDLE_SIZE)
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        # -- define additional instance vars --
        self.is_moving = False 
        self.is_at_initial_position = True
        # -- log instantiation --
        print(f"\n- New Window [Customer] Instance Created\n{'':2}- {self}")

    def __repr__(self):
        return f"Window For Customer : {self.my_customer.my_name}"
    
    def update(self):
        self.state_machine.update()

    def draw(self, screen):
        self.state_machine.draw(screen)

    def handle_events(self, event):
        self.state_machine.handle_events(event)


# ---- Window State : Parent Class ----
class WindowState:
    def __init__(self, window:CustomerWindow):
        self.window = window
        self.game = window.game

    def handle_events(self, event):
        ...

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
        ...

    def change_state_to_opened(self):
        self.window.state_machine.change_state(WindowStateOpened(self.window))
        self.window.state_machine.current_state.setup_open_window()
    
    def change_state_to_shelved(self):
        self.window.state_machine.change_state(WindowStateShelved(self.window))
        self.window.state_machine.current_state.setup_shelved_window()


# ---- Window States : Idle Child Class ----
class WindowStateIdle(WindowState):
    def __repr__(self):
        return f"Window State : Idling"

    def handle_events(self, event):
        ...
        # if event.type == pg.KEYDOWN:
        #     if event.key == pg.K_o:
        #         self.change_state_to_opened()
        #         print(f"Opening All Windows")

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
       ...
    

# ---- Window States : Opened Child Class ----
class WindowStateOpened(WindowState):
    default_open_win_positions = []

    def __repr__(self):
        return f"Window State : Opened"

    def handle_events(self, event):
        self.if_click_window_toggle_moving(event)
        self.if_moving_update_to_mouse_pos(event)

    def move_window(self, pos):
        self.window.rect.x, self.window.rect.y = pos

    def if_moving_update_to_mouse_pos(self, event):
        if event.type == pg.MOUSEMOTION:
            if self.window.is_moving:
                self.move_window(pg.mouse.get_pos())

    def check_if_hovered_titlebar(self):
        mx, my = pg.mouse.get_pos()
        titlebar_rect = self.window.rect.copy()
        titlebar_rect.h = 35
        if titlebar_rect.collidepoint(mx, my):
            self.window.image.fill(RED)
            
    def if_click_window_toggle_moving(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: # lmb
                if self.window.rect.collidepoint(event.pos):
                    self.window.is_moving = not self.window.is_moving
                    # -- new - also updates this bool to state when we have moved a window from its default opened position for ux as is expected functionality imo --
                    self.window.is_at_initial_position = False

    def create_and_wipe_open_window_image(self):
        self.window.image = pg.Surface(WIN_OPENED_SIZE)
        self.window.image.fill(CLEANORANGE)

    def create_window_titlebar(self):
        self.window_titlebar = pg.Surface((WIN_OPENED_SIZE[0], 35))
        self.window_titlebar.fill(BLUEMIDNIGHT)

    def draw_window_titlebar_to_window(self):
        self.window.image.blit(self.window_titlebar, (0, 0))

    def setup_open_window(self):
        """ create list of opened window positions for this level if we dont have it already, then create the image and set the initial window position """
        # -- note is only for when we move a window from the shelved position to opened --
        self.create_win_open_pos_class_list()
        self.create_and_wipe_open_window_image()
        self.calculate_and_set_initial_open_window_rect_pos()

    def calculate_and_set_initial_open_window_rect_pos(self):
        # -- get the list of all opened windows which are at the default opened position (i.e. havent been moved) --
        default_win_pos_arr = self.game.get_all_opened_default_pos_window_customers()
        if default_win_pos_arr:
            # -- get the next index by using the length of the array holding all opened window customers --
            next_customer_index = len(default_win_pos_arr) - 1 
            # -- use that index to set default window position rect, offsetting us from previously calculated default open positions --
            default_x = WindowStateOpened.default_open_win_positions[next_customer_index][0]
            default_y = WindowStateOpened.default_open_win_positions[next_customer_index][1]
            self.window.rect = pg.rect.Rect(default_x, default_y, WIN_OPENED_SIZE[0], WIN_OPENED_SIZE[1])

    def draw_user_name_to_titlebar(self):
        # -- guna be temp anyways, is dynamically place height regardless so can recycle this tbf --
        name_text_surf = self.game.FONT_W95FA_16.render(f"{self.window.my_customer.my_name} : {self.window.rect.x},{self.window.rect.y} : {self.window.is_at_initial_position}", True, WHITE) 
        self.window_titlebar.blit(name_text_surf, (10, int((35 - name_text_surf.get_height()) / 2)))

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
        self.create_and_wipe_open_window_image()
        self.create_window_titlebar()
        self.draw_user_name_to_titlebar()
        self.draw_window_titlebar_to_window()
        
        # [ low-key-critical ]
        #  => likely dont do like this tho btw, either decorator or as part of events (to set some bool only tho obvs, colour still set via draw function!)
        self.check_if_hovered_titlebar() 

    def create_win_open_pos_class_list(self):
        """ create list of all default positions for opened windows, 
        while creating that list when the window 'hits' (i.e. would be drawn at) 
        the bottom it goes back to the top and moves left by half a window w to add a nice, dynamic cascading effect """
        # -- should do this in game tbf then ensure it legitimately just runs once but this is fine for now, amkes changing to .game var obvs -- 
        if not WindowStateOpened.default_open_win_positions:
            increment_i = False
            x_increment, y_increment, y_multiplier = 0, 0, 0
            for i in range(self.game.game_level.customer_for_level):
                final_x, final_y = 50 * i, 50 * i
                # -- if we hit the bottom the current index becomes our increment index also --
                if final_y + WIN_OPENED_SIZE[1] > HEIGHT:    
                    if not increment_i:           
                        increment_i = i
                if increment_i: # dont div (well modulo but still...) but zero
                    y_increment = i % increment_i
                    if y_increment == 0:
                        y_multiplier += 1
                    y_increment = y_multiplier * (WIN_OPENED_SIZE[1] + 50) # window height plus 50
                    x_increment = y_multiplier * int(WIN_OPENED_SIZE[1] / 2) # so they cascade on top of each other, so you can ram in waaaay more (partly for stress testing, partly as would be funny to have a insanely stressful level lol)
                default_pos = (final_x - x_increment, final_y - y_increment)  
                WindowStateOpened.default_open_win_positions.append(default_pos)  

# ---- Window States : Shelved Child Class ----
class WindowStateShelved(WindowState):
    def __repr__(self):
        return f"Window For Customer {self.window.my_customer.my_name} : State = Shelved"

    def handle_events(self, event):
        ...
        # if event.type == pg.KEYDOWN:
        #     if event.key == pg.K_o:
        #         self.change_state_to_opened()

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
        self.create_and_wipe_shelved_window_image()
        self.draw_user_name_to_window()
       
    # ---- Additional Shelved State Methods ----
    
    def setup_shelved_window(self):
        self.create_and_wipe_shelved_window_image()
        self.calculate_and_set_shelved_window_rect_pos()

    def calculate_and_set_shelved_window_rect_pos(self):
        shelved_cust_count = len(self.game.get_all_shelved_window_customers())
        next_customer_index = shelved_cust_count - 1
        shelved_x = WIN_SHELVED_SIZE[0] * next_customer_index
        shelved_y = HEIGHT - 90 # 50 start bar + 40 chat bar
        # -- stack them if they reach the end --
        if shelved_x + WIN_SHELVED_SIZE[0] >= WIDTH:
            shelved_x = WIDTH - WIN_SHELVED_SIZE[0] 
            # self.game.desktop.is_shelved_overflowing = True # toggle this var which we'll use to create the overflow ui element
        self.window.rect = pg.rect.Rect(shelved_x, shelved_y, WIN_SHELVED_SIZE[0], WIN_SHELVED_SIZE[1])

    def create_and_wipe_shelved_window_image(self):
        self.window.image = pg.Surface(WIN_SHELVED_SIZE)
        self.window.image.fill(CLEANORANGE)

    def draw_user_name_to_window(self): # temp
        name_text_surf = self.game.FONT_W95FA_12.render(f"{self.window.my_customer.my_name} : {self.window.rect.x},{self.window.rect.y}", True, BLACK) 
        self.window.image.blit(name_text_surf, (10, int((35 - name_text_surf.get_height()) / 2)))


