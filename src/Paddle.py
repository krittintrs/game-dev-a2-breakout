import pygame
from src.constants import *
from src.Dependency import *
import random

class Paddle:
    def __init__(self, skin=1):
        self.x = WIDTH/2 - 96
        self.y = HEIGHT - 96

        self.dx = 0

        self.scale = 3
        self.width = self.scale * PADDLE_WIDTH_DEFAULT   # 64 * 3 (scale)
        self.height = self.scale * 16                    # 16 * 3 (scale)

        self.skin = skin
        self.isLarge = False
        self.SetImage()

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # self.mode = 'AI'  # Start in AI mode
        self.mode = 'PLAYER'

        # Blink effect variables
        self.blink_timer = 0
        self.blinking = False
        self.blink_interval = 0.2  # Time in seconds between blinks
        self.blink_duration = 1    # Total blink duration in seconds (1 sec blink)
        self.blink_time_remaining = 0

    def SetImage(self):
        if not self.isLarge:
            self.image = paddle_image_list[self.skin - 1]
        else:
            self.image = large_paddle_image_list[self.skin - 1]

    def Reset(self):
        self.DecreasePadSize()
        self.stop_blinking()
    
    def IncreasePadSize(self):
        self.isLarge = True
        self.width = self.scale * PADDLE_WIDTH_LARGE
        self.rect.width = self.width
        self.SetImage()

    def DecreasePadSize(self):
        self.isLarge = False
        self.width = self.scale * PADDLE_WIDTH_DEFAULT
        self.rect.width = self.width
        self.SetImage()

    def predict_ball_x(self, ball):
        """
        Predict where the ball will hit the paddle's y-position (bottom of the screen).
        """
        if ball.dy > 0:  # Only predict when the ball is moving down
            time_to_paddle = (self.y - ball.rect.y) / ball.dy
            predicted_x = ball.rect.x + ball.dx * time_to_paddle

            # Handle the ball bouncing off the walls
            if predicted_x < 0:
                predicted_x = -predicted_x
            elif predicted_x > WIDTH:
                predicted_x = WIDTH - (predicted_x - WIDTH)
            
            return predicted_x
        return ball.rect.x  # If the ball is moving upwards, no need to predict

    def update(self, dt, ball):
        if self.mode == 'PLAYER':
            # Player control logic (no changes)
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.dx = -PADDLE_SPEED
            elif key[pygame.K_RIGHT]:
                self.dx = PADDLE_SPEED
            else:
                self.dx = 0

            if self.dx < 0:
                self.rect.x = max(0, self.rect.x + self.dx * dt)
            else:
                self.rect.x = min(WIDTH - self.width, self.rect.x + self.dx * dt)

        # FIXME : convert back to human
        elif self.mode == 'AI':
            # AI control logic
            target_x = self.predict_ball_x(ball)

            if target_x < self.rect.x:
                self.dx = -PADDLE_SPEED
            elif target_x > self.rect.x + self.width:
                self.dx = PADDLE_SPEED
            else:
                self.dx = 0  # Already aligned

            # Smooth movement with speed limits
            if self.dx < 0:
                self.rect.x = max(0, self.rect.x + self.dx * dt)
            else:
                self.rect.x = min(WIDTH - self.width, self.rect.x + self.dx * dt)
        
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
        if self.blinking and self.blink_timer < self.blink_interval / 2:
            # During the first half of the blink interval, draw a white paddle
            pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=20)
        else:
            # Otherwise, draw the paddle's normal image
            screen.blit(self.image, (self.rect.x, self.rect.y))
