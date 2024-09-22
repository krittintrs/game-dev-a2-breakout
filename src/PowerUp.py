import pygame
from src.constants import *
from src.Dependency import *
from enum import Enum, auto

class PowerUpType(Enum):
    LASER_PADDLE = auto()
    EXTENDED_PADDLE = auto()
    BOMB_BALL = auto()

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 20  # Set appropriate size
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.type = power_type
        self.active = False  # Not yet activated
        self.speed = 150  # falling speed

        self.setImage()

    def setImage(self):
        if self.type == PowerUpType.BOMB_BALL:
            self.image = powerups_image_list[0]
        elif self.type == PowerUpType.EXTENDED_PADDLE:
            self.image = powerups_image_list[1]
        elif self.type == PowerUpType.LASER_PADDLE:
            self.image = powerups_image_list[2]
        
    def update(self, dt):
        """Move the power-up down."""
        self.y += self.speed * dt

    def render(self, screen):
        """Draw the power-up on the screen and display the name."""
        screen.blit(self.image, (self.x, self.y ))