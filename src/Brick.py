import pygame
from src.constants import *
from src.Dependency import *

brick_image_name_list = [
    "b_blue_0",
    "b_blue_1",
    "b_blue_2",
    "b_blue_3",
    "b_green_0",
    "b_green_1",
    "b_green_2",
    "b_green_3",
    "b_red_0",
    "b_red_1",
    "b_red_2",
    "b_red_3",
    "b_purple_0",
    "b_purple_1",
    "b_purple_2",
    "b_purple_3",
    "b_orange_0",
    "b_orange_1",
    "b_orange_2",
    "b_orange_3",
    "b_gray",
]

class Brick:
    def __init__(self, x, y):
        self.tier=0   # 0 - 3
        self.color=0  # 0 - 4

        self.x=x
        self.y=y

        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT

        self.alive = True
        self.unbreakable = False
        self.movable = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def Unbreaking(self):
        self.color = 5
        self.tier = 0
        self.unbreakable = True

    def Hit(self):
        if self.unbreakable:
            print('UNBREAK HIT!!!')
            # TODO: add sound
            # gSounds['brick-hit-unbreakable'].play()
        else:
            gSounds['brick-hit2'].play()
            
            if self.tier > 0:
                if self.color == 0:
                    self.tier = self.tier - 1
                    self.color = 4
                else:
                    self.color = self.color - 1

            else:
                if self.color == 0:
                    self.alive = False
                else:
                    self.color = self.color - 1

            if not self.alive:
                gSounds['brick-hit1'].play()

    def update(self, dt):
        pass

    def render(self, screen):
        if self.alive:
            screen.blit(
                brick_image_list[(self.color)*4 + self.tier], 
                (self.rect.x, self.rect.y)
            )