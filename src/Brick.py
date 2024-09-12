import pygame
from src.constants import *
from src.Dependency import *

brick_image_name_list = [
    "b_blue_1",
    "b_blue_2",
    "b_blue_3",
    "b_blue_4",
    "b_green_1",
    "b_green_2",
    "b_green_3",
    "b_green_4",
    "b_red_1",
    "b_red_2",
    "b_red_3",
    "b_red_4",
    "b_purple_1",
    "b_purple_2",
    "b_purple_3",
    "b_purple_4",
    "b_orange_1",
    "b_orange_2",
    "b_orange_3",
    "b_orange_4",
    "b_gray",
]

class Brick:
    def __init__(self, x, y):
        self.tier=0   #n->0
        self.color=1  #5->1

        self.x=x
        self.y=y

        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT

        self.alive = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def Hit(self):
        gSounds['brick-hit2'].play()
        print(f'\nhit brick >> tier: {self.tier} / color: {self.color} / image_idx: {brick_image_name_list[(self.color-1)*4 + self.tier]}')

        if self.tier > 0:
            if self.color == 1:
                self.tier = self.tier - 1
                self.color = 5
            else:
                self.color = self.color - 1

        else:
            if self.color == 1:
                self.alive = False
            else:
                self.color = self.color - 1

        if not self.alive:
            gSounds['brick-hit1'].play()

        print(f'          >> tier: {self.tier} / color: {self.color} / image_idx: {brick_image_name_list[(self.color-1)*4 + self.tier]}')


    def update(self, dt):
        pass

    def render(self, screen):
        if self.alive:
            screen.blit(
                brick_image_list[(self.color-1)*4 + self.tier], 
                (self.rect.x, self.rect.y)
            )