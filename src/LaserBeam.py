import pygame
from src.constants import *

class LaserBeam:
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT  # Start from the bottom of the screen
        self.width = 50
        self.height = HEIGHT  # Laser height will stretch from the paddle upwards

        # Timer for hit and blinking
        self.hit_timer = 0  # Accumulates time for hit intervals
        self.hit_interval = 0.5  # Every 0.5 seconds it can hit
        self.can_hit_now = False  # Toggle for hitting bricks
        self.color = (255, 255, 255)  # Default color (white)

        self.damage_timer = 0
        self.damage_interval = 0.3
        self.can_damage = False

        # Timer for staying after reaching top
        self.stay_time = 5  # Stays for 5 seconds after reaching top
        self.reached_top = False  # To track if the laser has reached the top

    def update(self, dt):
        # Move the laser upwards until it reaches the top
        if not self.reached_top:
            self.y -= 1000 * dt  # Adjust speed as needed
            if self.y <= 0:
                self.y = 0
                self.reached_top = True
                self.hit_timer = 0  # Reset the hit timer
        else:
            # Start countdown after reaching the top
            self.stay_time -= dt
            if self.stay_time <= 0:
                return False  # Mark the laser as done once time is up

        # Update the hit timer for blinking and hitting
        self.hit_timer += dt
        if self.hit_timer >= self.hit_interval:
            self.can_hit_now = not self.can_hit_now  # Toggle hit and blink status
            self.hit_timer = 0  # Reset the hit timer
            self.can_damage = True

        # Change color to red when it can hit, otherwise white
        if self.can_damage:
            self.damage_timer += dt
            if self.damage_timer >= self.damage_interval:
                self.can_damage = False
                self.damage_timer = 0
                self.color = (255, 255, 255)  # White color after hitting
            self.color = (255, 0, 0)  # Red color when able to hit
        else:
            self.color = (255, 255, 255)  # White color otherwise

        return True  # Laser is still active

    def can_hit(self):
        return self.can_hit_now

    def render(self, screen):
        # Draw the laser beam as a line with the current color (white or red)
        pygame.draw.line(screen, self.color, (self.x, HEIGHT), (self.x, self.y), self.width)
