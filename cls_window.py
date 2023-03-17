# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----

# ---- Imports ----
import pygame as pg
from random import choice

# ---- Internal Imports ----
from cls_state_machine import StateMachine
from settings import *


# -------- Window Classes --------
class Window(pg.sprite.Sprite):
    def __init__(self, game):
        # -- core setup --
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # -- additional instance vars --
        self.is_hovered = False


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
        self.is_hovered_titlebar = False
        self.is_hovered_minimise = False
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
        if not self.game.skip_remaining_windows: # so we dont do every single one after the one we clicked (due to the clicked state still technically being true)
            windex = self.window.state_machine.current_state.my_index
            self.window.state_machine.change_state(WindowStateOpened(self.window))
            self.window.state_machine.current_state.setup_open_window()
            self.update_shelved_index_positions(windex)
            self.game.skip_remaining_windows = True
            self.game.windows_layers.move_to_front(self.window)

    def update_shelved_index_positions(self, curr_index):
        shelved_cust_arr = self.game.get_all_shelved_window_customers()
        if shelved_cust_arr: # only do this if there is more than one shelved window before clicking to open one
            for a_cust in shelved_cust_arr:
                this_window = a_cust.my_window
                windex = this_window.state_machine.current_state.my_index
                if windex > curr_index:
                    a_cust.my_window.state_machine.current_state.my_index -= 1 # move the shelved windows down by 1 index position whenever we open a shelved window

    def change_state_to_shelved(self):
        self.window.state_machine.change_state(WindowStateShelved(self.window))
        self.window.state_machine.current_state.setup_shelved_window()


# ---- Window States : Idle Child Class ----
class WindowStateIdle(WindowState):
    def __repr__(self):
        return f"Window State : Idling"

    def handle_events(self, event):
        ...

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
       ...
    

# ---- Window States : Opened Child Class ----
class WindowStateOpened(WindowState):
    def __repr__(self):
        return f"Window State : Opened"

    def handle_events(self, event):
        self.if_click_titlebar_toggle_moving()
        self.if_moving_update_to_mouse_pos(event)

    def move_window(self, pos):
        self.window.rect.x, self.window.rect.y = pos

    def if_moving_update_to_mouse_pos(self, event):
        if event.type == pg.MOUSEMOTION:
            if self.window.is_moving:
                self.move_window(pg.mouse.get_pos())

    def check_if_hovered_minimise(self):
        mx, my = pg.mouse.get_pos()
        self.minimise_rect = self.window.rect.copy()
        self.minimise_rect.h = 25
        self.minimise_rect.w = 25
        self.minimise_rect.x = self.window.rect.x + self.window.image.get_width() - 30
        self.minimise_rect.y = self.window.rect.y
        if self.minimise_rect.collidepoint(mx, my):
            self.window.image.fill(YELLOW)
            self.window.is_hovered_minimise = True
        else:
            self.window.is_hovered_minimise = False

    def shelf_window_if_clicked_minimise_btn(self):
        if self.window.is_hovered_minimise:
            if self.game.mouse_click_up:
                self.change_state_to_shelved()

    def check_if_hovered_titlebar(self):
        mx, my = pg.mouse.get_pos()
        titlebar_rect = self.window.rect.copy()
        titlebar_rect.h = 35
        titlebar_rect.w -= 30
        if titlebar_rect.collidepoint(mx, my):
            self.window.image.fill(ORANGE)
            self.window.is_hovered_titlebar = True
        else:
            self.window.is_hovered_titlebar = False

    def update_moving_colour(self): # will likely update this once we have proper image stuff so its just an overlay alpha
        if self.window.is_moving:
            self.window.image.fill(GREEN) 
            
    def if_click_titlebar_toggle_moving(self):
        if self.window.is_hovered_titlebar:
            if self.game.mouse_click_up:
                self.window.is_moving = not self.window.is_moving
                # -- new - also updates this bool to state when we have moved a window from its default opened position for ux as is expected functionality imo --
                self.window.is_at_initial_position = False

    def create_and_wipe_open_window_image(self):
        self.window.image = pg.Surface(WIN_OPENED_SIZE)
        self.window.image.fill(CLEANORANGE)

    def create_minimise_btn_surf(self):
        self.window_titlebar_minimise_btn = pg.Surface((25, 25))
        self.window_titlebar_minimise_btn.fill(LIME)
    
    def draw_minimise_btn_to_titlebar(self):
        self.window_titlebar.blit(self.window_titlebar_minimise_btn, (WIN_OPENED_SIZE[0] - 30, 5))

    def create_window_titlebar(self):
        self.window_titlebar = pg.Surface((WIN_OPENED_SIZE[0], 35))
        self.window_titlebar.fill(BLUEMIDNIGHT)

    def draw_window_titlebar_to_window(self):
        self.window.image.blit(self.window_titlebar, (0, 0))

    def setup_open_window(self):
        """ create list of opened window positions for this level if we dont have it already, then create the image and set the initial window position """
        # -- note is only for when we move a window from the shelved position to opened --
        self.create_and_wipe_open_window_image()
        self.calculate_and_set_initial_open_window_rect_pos()

    def calculate_and_set_initial_open_window_rect_pos(self):
        # -- get the list of all opened windows which are at the default opened position (i.e. havent been moved) --
        default_win_pos_arr = self.game.get_all_opened_default_pos_window_customers()
        if default_win_pos_arr:
            # -- get the next index by using the length of the array holding all opened window customers --
            next_customer_index = len(default_win_pos_arr) - 1 
            # -- use that index to set default window position rect, offsetting us from previously calculated default open positions --
            default_x = self.game.default_open_win_positions[next_customer_index][0]
            default_y = self.game.default_open_win_positions[next_customer_index][1]
            self.window.rect = pg.rect.Rect(default_x, default_y, WIN_OPENED_SIZE[0], WIN_OPENED_SIZE[1])

    def draw_user_name_to_titlebar(self):
        # -- guna be temp anyways, is dynamically place height regardless so can recycle this tbf --
        name_text_surf = self.game.FONT_W95FA_16.render(f"{self.window.my_customer.my_name} : {self.window.rect.x},{self.window.rect.y} : {self.window.is_at_initial_position}", True, WHITE) 
        self.window_titlebar.blit(name_text_surf, (10, int((35 - name_text_surf.get_height()) / 2)))

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self):
        self.create_and_wipe_open_window_image()
        self.check_if_hovered_titlebar() 
        self.check_if_hovered_minimise()
        self.create_window_titlebar()
        self.create_minimise_btn_surf()
        self.draw_minimise_btn_to_titlebar()
        self.draw_user_name_to_titlebar()
        self.draw_window_titlebar_to_window()
        self.update_moving_colour()
        self.shelf_window_if_clicked_minimise_btn()


# ---- Window States : Shelved Child Class ----
class WindowStateShelved(WindowState):
    def __repr__(self):
        return f"Window For Customer {self.window.my_customer.my_name} : State = Shelved"

    def handle_events(self, event):
        ...

    def draw(self, screen:pg.Surface):
        ...
    
    def update(self): 
        self.set_shelved_window_rect_pos()
        self.highlight_on_hover()
        self.create_and_wipe_shelved_window_image()
        self.draw_user_name_to_window()
        self.open_on_click()

    # ---- Additional Shelved State Methods ----

    def highlight_on_hover(self):
        """ previously was a parent method, could have just overridden it but since dont need for idle state simply abstracting it out properly instead """
        self.window.is_hovered = False
        if self.window.rect.collidepoint(pg.mouse.get_pos()):
            self.window.is_hovered = True
            
    def open_on_click(self):
        if self.window.is_hovered:
            if self.game.mouse_click_up:
                    self.change_state_to_opened()

    def setup_shelved_window(self):
        self.create_and_wipe_shelved_window_image()
        self.calculate_shelved_index()

    def calculate_shelved_index(self):
        shelved_cust_count = len(self.game.get_all_shelved_window_customers())
        next_customer_index = shelved_cust_count - 1
        self.my_index = next_customer_index

    def set_shelved_window_rect_pos(self):
        shelved_x = WIN_SHELVED_SIZE[0] * self.my_index
        shelved_y = HEIGHT - 90 # startbar which is 50px plus chatbar which is 40px
        # -- stack them if they reach the end --
        if shelved_x + WIN_SHELVED_SIZE[0] >= WIDTH:
            shelved_x = WIDTH - WIN_SHELVED_SIZE[0] 
        self.window.rect = pg.rect.Rect(shelved_x, shelved_y, WIN_SHELVED_SIZE[0], WIN_SHELVED_SIZE[1])

    def create_and_wipe_shelved_window_image(self):
        self.window.image = pg.Surface(WIN_SHELVED_SIZE)
        if self.window.is_hovered:
            self.window.image.fill(HIGHLIGHTER)
        else:
            self.window.image.fill(CLEANORANGE)

    def draw_user_name_to_window(self): # temp
        name_text_surf = self.game.FONT_W95FA_12.render(f"{self.window.my_customer.my_name} : {self.window.rect.x},{self.window.rect.y}", True, BLACK) 
        self.window.image.blit(name_text_surf, (10, int((35 - name_text_surf.get_height()) / 2)))


