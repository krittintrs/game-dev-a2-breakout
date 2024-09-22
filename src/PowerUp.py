import pygame
from src.constants import *
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
        self.font = pygame.font.Font(None, 24)  # Font for debugging text

    def update(self, dt):
        """Move the power-up down."""
        self.y += self.speed * dt

    def render(self, screen):
        """Draw the power-up on the screen and display the name."""
        if self.type == PowerUpType.LASER_PADDLE:
            # Draw laser paddle power-up (example color)
            pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))
            power_up_name = "Laser Paddle"
        elif self.type == PowerUpType.EXTENDED_PADDLE:
            # Draw extended paddle power-up (example color)
            pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))
            power_up_name = "Extended Paddle"
        elif self.type == PowerUpType.BOMB_BALL:
            # Draw bomb ball power-up (example color)
            pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.width, self.height))
            power_up_name = "Bomb Ball"

        # Render the power-up name below the power-up
        label = self.font.render(power_up_name, True, (255, 255, 255))  # White color text
        screen.blit(label, (self.x, self.y + self.height + 5))  # Adjust position below the power-up
