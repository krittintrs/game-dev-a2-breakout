import pygame
from src.constants import *

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0  # Start with no radius
        self.max_radius = BOMB_RANGE  # Maximum explosion radius
        self.expanding = True
        self.timer = 0
        self.duration = 4  # Duration of the fading effect in seconds
        self.start_time = pygame.time.get_ticks()  # Track when the explosion started

    def update(self, dt):
        if self.expanding:
            self.radius += 3  # Increase radius
            if self.radius >= self.max_radius:
                self.expanding = False
                self.start_time = pygame.time.get_ticks()  # Start timer for fading
        else:
            self.timer += dt
            if self.timer >= self.duration:
                return False  # Mark explosion as done
        return True  # Explosion is still active

    def render(self, screen):
        if self.expanding:
            # Draw a simple circle for the explosion
            pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)
        else:
            # Draw a fading effect
            elapsed_time = pygame.time.get_ticks() - self.start_time  # Get elapsed time since expanding
            alpha = max(0, 255 - (255 * elapsed_time / (self.duration * 1000)))  # Calculate alpha
            
            fade_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA) 
            fade_surface.fill((0, 0, 0, 0))  # Fill with transparent color
            explosion_color = (255, 0, 0, alpha)
            pygame.draw.circle(fade_surface, explosion_color, (self.radius, self.radius), self.radius)  # Centered on surface
            screen.blit(fade_surface, (self.x - self.radius, self.y - self.radius))
