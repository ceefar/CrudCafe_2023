# ---- Crud Cafe v1.00 ----
# ---- By Courtney "Ceefar" Farquharson ----

# ---- Imports ----
import pygame as pg

# ---- Internal Imports ----
from settings import *


# ---- StartBar : Parent Class ----
class StartBar(pg.sprite.Sprite): 
    def __init__(self, game):
        # -- core setup --
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # -- setup default rect and image --
        self.image = pg.Surface((WIDTH, 50))
        self.image.fill(SILVER)
        self.rect = pg.rect.Rect(0, HEIGHT - 50, WIDTH, 40)
    
    def draw_start_icon_to_start_bar(self):
        self.start_icon = self.game.win95_start_btn
        self.image.blit(self.start_icon, (5, 5))     
    
    def wipe_image(self):
        self.image.fill(SILVER)

    def update(self):
        self.wipe_image()
        self.draw_start_icon_to_start_bar()

    def draw(self, screen:pg.Surface):
        screen.blit(self.image, self.rect)