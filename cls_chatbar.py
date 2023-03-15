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
        self.is_shelved_overflowing = False # < test var
    
    def draw(self, screen:pg.Surface):
        screen.blit(self.image, self.rect)