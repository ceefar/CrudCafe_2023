# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----

# ---- Imports ----
import pygame as pg
import sys
from os import path

# ---- internal Imports ----
from cls_state_machine import StateMachine
from cls_desktop import Desktop, DesktopState, DesktopStateIdle, DesktopStateInfo, DesktopStateOrdersMenu
from cls_customer import Customer, CustomerState, CustomerStateCancelled, CustomerStateCompleted, CustomerStateOrdering, CustomerStateQueueing
from cls_window import Window, CustomerWindow, InfoWindow, WindowState, WindowStateIdle, WindowStateOpened, WindowStateShelved
from cls_gamelevel import GameLevel_1, GameLevel_2, GameLevel_3
from cls_chatbar import ChatBar, OverflowElement
from cls_startbar import StartBar
from settings import *


# ---- Game Class ----
class Game:
    def __init__(self):
        """ initialise the main pygame game class """
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        self.game_folder = path.dirname(__file__)


    # ---- Create & Load ----

    def load_data(self):
        self.load_fonts()
        self.load_images()
        self.create_core_vars()
        self.create_additional_vars()
        self.create_groups()
        self.create_layers()
        self.create_chatbar()
        self.create_overflow_element()
        self.create_startbar()
        self.create_desktop()

    def create_startbar(self):
        self.startbar = StartBar(self)
        self.startbar_layer.add(self.startbar) 
        # as per desktop layer, may need to bring forward

    def create_overflow_element(self):
        self.overflow_element = OverflowElement(self)
        self.overflow_layer.add(self.overflow_element) 

    def create_chatbar(self):
        self.chatbar = ChatBar(self)
        self.chatbar_layer.add(self.chatbar) 
        # as per desktop layer, may need to bring forward

    def create_desktop(self):
        self.desktop = Desktop(self)
        self.desktop_layer.add(self.desktop) 
        self.desktop_layer.change_layer(self.desktop, 0) 

    def create_groups(self):
        """ potentially can remove this btw, potentially just to replace entirely by layers """
        self.all_sprites = pg.sprite.Group()
        self.all_customers = pg.sprite.Group()

    def create_layers(self):
        self.desktop_layer = pg.sprite.LayeredUpdates() # always layer 0/1 (the back-est layer)
        self.chatbar_layer = pg.sprite.LayeredUpdates() # always behind windows
        self.startbar_layer = pg.sprite.LayeredUpdates() # always behind windows
        self.windows_layers = pg.sprite.LayeredUpdates() # always behind overflow layer
        self.overflow_layer = pg.sprite.LayeredUpdates() # always the toppest

    def create_core_vars(self):
        self.current_level = 0

    def create_additional_vars(self):
        self.skip_remaining_customers = False
        self.skip_remaining_windows = False
        self.default_open_win_positions = []

    def setup_level(self):
        # -- set the initial level - game level basically behaves like a simple dataclass --
        if self.current_level == 0:
            self.game_level = GameLevel_1
        # -- run core level setup --
        self.create_windows_for_level()
        # --
        self.create_win_open_pos_class_list()
        # -- log success --
        print(f"\n- Level Setup Completed")
        print(f"\n- Starting Game...\n")

    def create_windows_for_level(self):
        for i in range(self.game_level.customer_for_level):
            new_customer = Customer(self, i)
            new_window = CustomerWindow(self, new_customer)
            new_customer.add_window_to_customer_instance(new_window)
            self.windows_layers.add(new_window)
        

    # ---- New ----

    def get_all_opened_window_customers(self) -> Customer|None:
        all_opened_customers = list(filter(lambda x: x if isinstance(x.my_window.state_machine.current_state, WindowStateOpened) else 0, self.all_customers))
        return all_opened_customers if all_opened_customers else None
    
    def get_all_opened_default_pos_window_customers(self) -> Customer|None:
        all_opened_customers = list(filter(lambda x: x if isinstance(x.my_window.state_machine.current_state, WindowStateOpened) and x.my_window.is_at_initial_position else 0, self.all_customers))
        return all_opened_customers if all_opened_customers else None
    
    def get_all_shelved_window_customers(self) -> Customer|None:
        all_shelved_customers = list(filter(lambda x: x if isinstance(x.my_window.state_machine.current_state, WindowStateShelved) else 0, self.all_customers))
        return all_shelved_customers if all_shelved_customers else None
        

    # ---- Draw, Run, Updates, Events ----

    def draw(self):
        # -- set caption --
        pg.display.set_caption(f"Crud Cafe v1.00 - {self.clock.get_fps():.2f}")
        # -- wipe the screen so its blank, then run desktop draw functions --
        self.screen.fill(WHITE)
        self.desktop.draw(self.screen)
        self.startbar.draw(self.screen)
        self.chatbar.draw(self.screen)
        # -- draw layered sprites uing layers objects to draw things that require layering in the correct order --
        self.windows_layers.draw(self.screen)
        self.overflow_layer.draw(self.screen) # order of operations matters rn as windows arent layered, wont once thats added tho
        # -- flip display to end --
        pg.display.flip()

    def update(self):
        self.desktop.update()
        self.startbar.update()
        self.update_overflow()
        self.overflow_layer.update()
        self.windows_layers.update()
        self.reset_update_vars()

    def update_overflow(self):
        overflowing_tally = 0
        for a_customer in self.all_customers:
            if a_customer.my_window.rect.x >= WIDTH - 100:
                self.chatbar.is_shelved_overflowing = True   
                overflowing_tally += 1
                self.overflow_element.update_tally(overflowing_tally)

    def create_win_open_pos_class_list(self):
        """ create list of all default positions for opened windows, 
        while creating that list when the window 'hits' (i.e. would be drawn at) 
        the bottom it goes back to the top and moves left by half a window w to add a nice, dynamic cascading effect """
        # -- should do this in game tbf then ensure it legitimately just runs once but this is fine for now, amkes changing to .game var obvs -- 
        if not self.default_open_win_positions:
            increment_i = False
            x_increment, y_increment, y_multiplier = 0, 0, 0
            for i in range(self.game_level.customer_for_level):
                final_x, final_y = 50 * i, 50 * i
                # -- if we hit the bottom the current index becomes our increment index also --
                if final_y + 400 > HEIGHT: # WIN_OPENED_SIZE[1]
                    if not increment_i:           
                        increment_i = i
                if increment_i: # dont div (well modulo but still...) but zero
                    y_increment = i % increment_i
                    if y_increment == 0:
                        y_multiplier += 1
                    y_increment = y_multiplier * (400 + 50) # window height plus 50  # WIN_OPENED_SIZE[1]
                    x_increment = y_multiplier * int(400 / 2) # WIN_OPENED_SIZE[1]  # so they cascade on top of each other, so you can ram in waaaay more (partly for stress testing, partly as would be funny to have a insanely stressful level lol)
                default_pos = (final_x - x_increment, final_y - y_increment)  
                self.default_open_win_positions.append(default_pos)  

    def reset_update_vars(self):
        """ self referencing af but is for finally reset any necessary toggle vars """
        self.skip_remaining_customers = False
        self.skip_remaining_windows = False

    def run(self):
        # -- run setup --
        game.setup_level()
        # -- run main game loop --
        while True:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def events(self):
        # -- define and reset mouse states each frame -- 
        self.mouse_click_up, self.mouse_click_down, self.mouse_scroll_up, self.mouse_scroll_down = False, False, False, False
        # -- handle events --
        for event in pg.event.get():
            # -- handle quit events first --
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            # -- handle press esc to quit --
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
            # -- mouse events - mouse down --
            if event.type == pg.MOUSEBUTTONDOWN: 
                if event.button == 1:  # left click
                    self.mouse_click_down = True
            # -- mouse events - mouse up --
            if event.type == pg.MOUSEBUTTONUP: 
                if event.button == 4:  # scroll up
                    self.mouse_scroll_up = True                          
                elif event.button == 5:  # scroll down
                    self.mouse_scroll_down = True                    
                elif event.button == 1:  # left click
                    self.mouse_click_up = True
            # -- then handle any keyboard or mouse events for object instances next --
            self.desktop.handle_events(event)
            # -- use list comprehensions to loop to handle customer and window events --
            [a_customer.handle_events(event) for a_customer in self.all_customers]
            [a_window.handle_events(event) for a_window in self.windows_layers]
                

    def display_game_start_screen(self):
        ...


    # ---- Additonal x Miscellaneous Methods ----

    def load_fonts(self):
        """ preload fonts, could be done incrementally but only needs to run once at the start and isn't expensive as a one off so this is fine, also should probably be in the load section but clogs up the code editor """
        fonts_folder = path.join(self.game_folder, 'fonts')
        # -- windows 95 style font --
        self.FONT_W95FA_10 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 10)
        self.FONT_W95FA_12 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 12)
        self.FONT_W95FA_14 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 14)
        self.FONT_W95FA_16 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 16)
        self.FONT_W95FA_18 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 18)
        self.FONT_W95FA_20 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 20)
        self.FONT_W95FA_22 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 22)
        self.FONT_W95FA_24 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 24)
        self.FONT_W95FA_26 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 26)
        self.FONT_W95FA_28 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 28)
        self.FONT_W95FA_30 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 30)
        self.FONT_W95FA_32 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 32)
        self.FONT_W95FA_48 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 48)
        self.FONT_W95FA_64 = pg.font.Font((path.join(fonts_folder, "W95FA.otf")), 64)

    def load_images(self):
        imgs_folder = path.join(self.game_folder, 'imgs')
        self.win95_start_btn = pg.image.load(path.join(imgs_folder, "win95_start_btn_1.png")).convert_alpha()         
        self.win95_start_btn = pg.transform.scale(self.win95_start_btn, (94, 40)) # 117, 50  # 94, 40  # 70.5, 30

# -- create new game instance and run the game --
if __name__ == "__main__":
    game = Game()
    game.load_data()
    game.display_game_start_screen()
    while True:
        game.run()



# done 
# -----
# - stackable overflow sidebar 
# - when opening one window have the shelved reposition
# - windows brought to front when moved from shelved to opened
# - add click to move via titlebar only
# - added minimise btn, no functionality tho
# - proper interactions on titlebar, i.e. titlebar and minimise btn interactivity is entirely seperate and working when moving the windows
# - added click to minimise button with functionality and ensured doesnt clash with titlebar click interaction (which moves the window) 


# current
# -------
# - proper opened windows stuff
#   - zerothindex layer stuff now 100!
#      - remember dont use the 0th / 1st layer
#      - and ensure set desktop to layer 0/1 
#       - confirm this is all good using startbar and else btw?!
#   - click to bring to front when opened (if not click titlebar)
#       - check existing code, consider small refactor if too many checks
#   - sort the hover effects
#   - light stylise if not done already
#       - including clickable bar only for move
#       - minimise button, etc
# 
# - windowText class stuff?
#
# - try info window quickly?

# OMG PLS PLS PLS
# - add db thing to this
# - add aws functionality too
# - maybe even a docker (nah but tuts tho)


# USER CUSTOMER ORDER CLASS!!!
# - and ffs a better name pls XD

# then bg setup, then start game screen and level flow and tutorial stuff!
#   - then likely re-refactor that (since its so early its worth it imo)

# - so lets have a start screen from the start even if it does nothing
# - lets also have user name input

# - then do moving windows and stackable windows stuff from the start full clean af
#   - note : the desktop layer is infront of everything else except the windows which can be on top

# - game level 0 loads and we'll have some tutorial ting setup 
#   - literally just one for the start
#       - i.e. welcome to the first day on the job, take orders, good luck
#   - then from there its literally stuff like
#       - looks like you've got a new customer!