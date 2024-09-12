import pygame
from src.constants import *
from src.Dependency import *
import random

class Paddle:
    def __init__(self, skin=1):
        self.x = WIDTH/2 - 96
        self.y = HEIGHT - 96

        self.dx = 0

        self.size = 2

        self.width = self.size * 96 # 2 * 32 * 3 (scale)
        self.height = 48   # 16 * 3 (scale)

        self.SetImage(skin)

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.mode = 'AI'  # Start in AI mode
        # self.mode = 'PLAYER'

    def SetImage(self, skin):
        self.skin = skin
        self.image = paddle_image_list[self.skin - 1]

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

    def render(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
