# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----

# ---- Imports ----
import pygame as pg

# ---- Internal Imports ----
from settings import *


# ---- ChatBar : Parent Class ----
class ChatBar(pg.sprite.Sprite): 
    def __init__(self, game):
        # -- core setup --
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # -- setup default rect and image --
        self.image = pg.Surface((WIDTH, 40))
        self.image.fill(BLUEMIDNIGHT)
        self.rect = pg.rect.Rect(0, HEIGHT - 90, WIDTH, 40)
        # -- setup general vars --
        self.is_shelved_overflowing = False  # toggles on or off the overflowing chatbar ui element
    
    def draw(self, screen:pg.Surface):
        screen.blit(self.image, self.rect)


# ---- Overflow Element : Parent Class ----
class OverflowElement(pg.sprite.Sprite): 
    def __init__(self, game):
        # -- core setup --
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # -- create image and rect but set the rect to offscreen initially so we dont draw it from the off --
        self.create_image()
        self.rect = pg.rect.Rect(-100, -100, 0, 0)

    def create_image(self):
        self.image = pg.Surface(WIN_SHELVED_SIZE) 
        self.image.fill(RED)

    def create_rect(self):
        rect_x = WIDTH - WIN_SHELVED_SIZE[0]  # could change from tuple to vec2 to use xy but isnt a big deal as no compatability issues
        rect_y = HEIGHT - 90 # once element is 50 and one is 40 will hardcode as Constants eventually but this will do for now as is a static element
        self.rect = pg.rect.Rect(rect_x, rect_y, WIN_SHELVED_SIZE[0], WIN_SHELVED_SIZE[1])
    
    def update_tally(self, curr_tally):
        self.tally = curr_tally

    def draw_tally_to_img(self):
        tally_text_surf = self.game.FONT_W95FA_18.render(f"{self.tally}", True, RED) 
        text_x = int((self.bg_rect.width - tally_text_surf.get_width()) / 2) + 2
        text_y = int((self.bg_rect.height - tally_text_surf.get_height()) / 2) + 2
        self.image.blit(tally_text_surf, (text_x, text_y)) # dynamically positioned in center

    def draw_info_text_to_img(self):
        info_text_surf = self.game.FONT_W95FA_18.render(f"More", True, WHITE) 
        text_y = int((self.bg_rect.height - info_text_surf.get_height()) / 2) + 2
        self.image.blit(info_text_surf, (35, text_y))

    def draw_bg_rect_for_tally_text(self):
        self.bg_rect = pg.rect.Rect(2, 2, 26, 36)
        pg.draw.rect(self.image, WHITE, self.bg_rect)
        
    def update(self):
        if self.game.chatbar.is_shelved_overflowing:
            self.game.overflow_layer.move_to_front(self)
            self.create_image()
            self.draw_bg_rect_for_tally_text()
            self.draw_tally_to_img()
            self.draw_info_text_to_img()
            self.create_rect()


# Notes
# --------
# then obvs will handle hover and click for this seperately 
# and will make showing the customers hidden under here (just use their pos) hella easy as will handle everything here
#   - will in a new class tbf but as part of OverflowElement module (if wanna move this, could keep it here tho tbf)
