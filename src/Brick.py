import pygame
from src.constants import *
from src.Dependency import *
import src.tween as tween
import random

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

        # Blink effect variables
        self.blink_timer = 0
        self.blinking = False
        self.blink_interval = 0.2  # Time in seconds between blinks
        self.blink_duration = 1    # Total blink duration in seconds (1 sec blink)
        self.blink_time_remaining = 0

    def Unbreaking(self):
        self.color = 5
        self.tier = 0
        self.unbreakable = True

    def Moving(self, start_x, end_x):
        self.Unbreaking()
        self.movable = True

        x_diff = self.x - start_x
        total_diff = end_x - start_x
        ratio = x_diff / total_diff

        def initial_move_right():
            tween.to(self.rect, 'x', end_x - self.width, 
                     MOVING_BRICK_TIMER*(1-ratio)).on_complete(move_left)
        def initial_move_left():
            tween.to(self.rect, 'x', start_x, 
                     MOVING_BRICK_TIMER*ratio).on_complete(move_right)
        def move_right():
            tween.to(self.rect, 'x', end_x - self.width, 
                     MOVING_BRICK_TIMER).on_complete(move_left)
        def move_left():
            tween.to(self.rect, 'x', start_x, 
                     MOVING_BRICK_TIMER).on_complete(move_right)

        if random.choices([True, False]):
            initial_move_right()
        else:
            initial_move_left()

    def Hit(self):
        if self.unbreakable:
            gSounds['brick-hit-unbreakable'].play()
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
                return True
            
        return False

    def update(self, dt):
        if self.movable:
            tween.update(dt)
        
        # Handle blinking effect timer
        if self.blinking:
            self.blink_timer += dt
            self.blink_time_remaining -= dt
            if self.blink_time_remaining <= 0:
                self.blinking = False  # Stop blinking after 1 second

            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0  # Reset the blink interval timer

    def start_blinking(self):
        """Start the blinking effect."""
        self.blinking = True
        self.blink_timer = 0
        self.blink_time_remaining = self.blink_duration

    def stop_blinking(self):
        """Stop the blinking effect."""
        self.blinking = False
        self.blink_timer = self.blink_interval
        self.blink_time_remaining = 0
        
    def render(self, screen):
        if self.alive:
            if self.blinking and self.blink_timer < self.blink_interval / 2:
                # During the first half of the blink interval, draw a white paddle
                pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=20)
            else:
                screen.blit(
                    brick_image_list[(self.color)*4 + self.tier], 
                    (self.rect.x, self.rect.y)
                )