import random, pygame, sys
from src.states.BaseState import BaseState
from src.constants import *
from src.Dependency import *
import src.CommonRender as CommonRender

class PlayState(BaseState):
    def __init__(self):
        super(PlayState, self).__init__()
        self.paused = False

    def Enter(self, params):
        self.paddle = params['paddle']
        self.bricks = params['bricks']
        self.health = params['health']
        self.score = params['score']
        self.high_scores = params['high_scores']
        self.ball = params['ball']
        self.level = params['level']

        self.power_ups = []
        self.power_up_timers = {}
        self.paddle.Reset()
        self.explosions = []
        self.lasers = []

        self.recover_points = 5000

        self.ball.dx = random.randint(-600, 600)  # -200 200
        self.ball.dy = random.randint(-180, -150)


    def update(self,  dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    gSounds['pause'].play()
                    #music_channel.play(sounds_list['pause'])
                if event.key == pygame.K_k:
                    gSounds['victory'].play()

                    g_state_manager.Change('victory', {
                        'level':self.level,
                        'paddle':self.paddle,
                        'health':self.health,
                        'score':self.score,
                        'high_scores':self.high_scores,
                        'ball':self.ball,
                        'recover_points':self.recover_points
                    })

        if self.paused:
            return

        self.paddle.update(dt, self.ball)
        self.ball.update(dt)

        if self.ball.Collides(self.paddle):
            # raise ball above paddle
            ####can be fixed to make it natural####
            self.ball.rect.y = self.paddle.rect.y - self.ball.rect.height
            self.ball.dy = -self.ball.dy

            # half left hit while moving left (side attack) the more side, the faster
            if self.ball.rect.x + self.ball.rect.width < self.paddle.rect.x + (self.paddle.width / 2) and self.paddle.dx < 0:
                self.ball.dx = -150 + -(8 * (self.paddle.rect.x + self.paddle.width / 2 - self.ball.rect.x))
            # right paddle and moving right (side attack)
            elif self.ball.rect.x > self.paddle.rect.x + (self.paddle.width / 2) and self.paddle.dx > 0:
                self.ball.dx = 150 + (8 * abs(self.paddle.rect.x + self.paddle.width / 2 - self.ball.rect.x))
            gSounds['paddle-hit'].play()

        for i, brick in enumerate(self.bricks):
            brick.update(dt)
            if brick.alive and self.ball.Collides(brick):
                if not brick.unbreakable:
                    self.score = self.score + (brick.tier * 200 + (brick.color+1) * 25)
                    # print(self.score)
                
                # Bomb ball effect
                if self.ball.isBomb:
                    gSounds['bomb'].play()

                    if not brick.unbreakable:
                        # Calculate score for the brick
                        # print(f'Brick color: {brick.color}, Brick tier: {brick.tier}')
                        color_score = [25, 50, 75, 100, 125]
                        current_tier_score = sum(color_score[:brick.color + 1])
                        if brick.tier > 0:
                            current_tier_inc = brick.tier * 200 * (brick.color + 1)
                            current_tier_score += current_tier_inc
                            tier_score = [375, 1375, 2375, 3375]
                            prev_tier_score = sum(tier_score[:brick.tier])
                        else:
                            prev_tier_score = 0
                        # print(f'Current tier score: {current_tier_score} = {sum(color_score[:brick.color + 1])} + {current_tier_inc}, Previous tier score: {prev_tier_score}')
                        bomb_score = 250
                        self.score += current_tier_score + prev_tier_score + bomb_score
                        brick.alive = False
                        isDestroyed = True
                    else:
                        isDestroyed = False

                    # Destroy nearby bricks
                    for other_brick in self.bricks:
                        if other_brick.alive and other_brick != brick:
                            distance_x_left = self.ball.rect.centerx - other_brick.rect.x
                            distance_x_right = self.ball.rect.centerx - (other_brick.rect.x + other_brick.width)
                            distance_y_top = self.ball.rect.centery - other_brick.rect.y   
                            distance_y_bottom = self.ball.rect.centery - (other_brick.rect.y + other_brick.height)  
                            distance_1 = (distance_x_left ** 2 + distance_y_top ** 2) ** 0.5
                            distance_2 = (distance_x_right ** 2 + distance_y_top ** 2) ** 0.5
                            distance_3 = (distance_x_left ** 2 + distance_y_bottom ** 2) ** 0.5
                            distance_4 = (distance_x_right ** 2 + distance_y_bottom ** 2) ** 0.5
                            if distance_1 < BOMB_RANGE or distance_2 < BOMB_RANGE or distance_3 < BOMB_RANGE or distance_4 < BOMB_RANGE:
                                isBombDestroyed = other_brick.Hit()
                                other_brick.start_blinking()
                                self.score += (other_brick.tier * 200 + (other_brick.color + 1) * 25)
                                if isBombDestroyed:
                                    self.spawn_powerup(brick)
                    
                    explosion = Explosion(self.ball.rect.centerx, self.ball.rect.centery)
                    self.explosions.append(explosion)
                    self.ball.StopBombBall()
                else:
                    isDestroyed = brick.Hit()

                # if brick is destoryed, may spawn power-up
                if isDestroyed:
                    self.spawn_powerup(brick)

                # recovery health
                if self.score > self.recover_points:
                    self.health = min(3, self.health + 1)
                    self.recover_points = min(100000, self.recover_points * 2)

                    gSounds['recover'].play()
                    #music_channel.play(sounds_list['recover'])

                # check if all bricks are destroyed
                if self.CheckVictory():
                    gSounds['victory'].play()

                    for power_up in self.power_ups:
                        self.deactivate_powerup(power_up.type)

                    g_state_manager.Change('victory', {
                        'level':self.level,
                        'paddle':self.paddle,
                        'health':self.health,
                        'score':self.score,
                        'high_scores':self.high_scores,
                        'ball':self.ball,
                        'recover_points':self.recover_points
                    })

                # hit brick from left while moving right -> x flip
                if self.ball.rect.x + 6 < brick.rect.x and self.ball.dx > 0:
                    self.ball.dx = -self.ball.dx
                    self.ball.rect.x = brick.rect.x - 24

                # hit brick from right while moving left -> x flip
                elif self.ball.rect.x + 18 > brick.rect.x + brick.width and self.ball.dx < 0:
                    self.ball.dx = -self.ball.dx
                    self.ball.rect.x = brick.rect.x + 96

                # hit from above -> y flip
                elif self.ball.rect.y < brick.rect.y:
                    self.ball.dy = -self.ball.dy
                    self.ball.rect.y = brick.rect.y - 24

                # hit from bottom -> y flip
                else:
                    self.ball.dy = -self.ball.dy
                    self.ball.rect.y = brick.rect.y + 48

                # whenever hit, speed is slightly increase, maximum is 450
                if abs(self.ball.dy) < 450:
                    self.ball.dy = self.ball.dy * 1.02

                break
        
        # if paddle misses the ball
        if self.ball.rect.y >= HEIGHT:
            self.health -= 1
            gSounds['hurt'].play()

            for power_up in self.power_ups:
                self.deactivate_powerup(power_up.type)

            if self.health == 0:
                g_state_manager.Change('game-over', {
                    'score':self.score,
                    'high_scores': self.high_scores
                })
            else:
                g_state_manager.Change('serve', {
                    'level': self.level,
                    'paddle': self.paddle,
                    'bricks': self.bricks,
                    'health': self.health,
                    'score': self.score,
                    'high_scores': self.high_scores,
                    'recover_points': self.recover_points
                })

        # Update power-ups
        for power_up in self.power_ups:
            power_up.update(dt)

            # Check if power-up is collected by the paddle
            if self.check_powerup_collision(self.paddle, power_up):
                # print(f"Power-up {power_up} collected")
                self.power_ups.remove(power_up)

            # Remove power-up if it falls off the screen
            elif power_up.y > HEIGHT:
                self.power_ups.remove(power_up)

        # Update timers for active power-ups
        for power_up_type, time_left in list(self.power_up_timers.items()):
            self.power_up_timers[power_up_type] -= dt
            if self.power_up_timers[power_up_type] <= 0:
                self.deactivate_powerup(power_up_type)
                del self.power_up_timers[power_up_type]

        # Update explosions
        for explosion in self.explosions:
            if not explosion.update(dt):
                self.explosions.remove(explosion)

        # Update lasers
        for laser in self.lasers:
            if not laser.update(dt):
                self.lasers.remove(laser)  # Remove the laser if it has expired
                continue

            # If the laser can hit (every 0.5 seconds)
            if laser.can_hit():
                gSounds['laser_shoot'].play()
                for brick in self.bricks:
                    # Check if the laser intersects with the brick
                    if brick.rect.x > laser.x + laser.width or brick.rect.x + brick.width < laser.x:
                        continue
                    else:
                        if brick.alive and not brick.unbreakable:
                            isLaserDestroyed = brick.Hit()
                            brick.start_blinking()
                            self.score += (brick.tier * 200 + (brick.color + 1) * 25)
                            if isLaserDestroyed:
                                self.spawn_powerup(brick)
                    
                    if self.CheckVictory():
                        gSounds['victory'].play()

                        for power_up in self.power_ups:
                            self.deactivate_powerup(power_up.type)

                        g_state_manager.Change('victory', {
                            'level':self.level,
                            'paddle':self.paddle,
                            'health':self.health,
                            'score':self.score,
                            'high_scores':self.high_scores,
                            'ball':self.ball,
                            'recover_points':self.recover_points
                        })
                laser.can_hit_now = False  # Reset the hit status

    def Exit(self):
        pass

    def render(self, screen):
        for brick in self.bricks:
            brick.render(screen)
        
        # Render power-ups
        for power_up in self.power_ups:
            power_up.render(screen)

        for explosion in self.explosions:
            explosion.render(screen)

        for laser in self.lasers:
            laser.render(screen)

        self.paddle.render(screen)
        self.ball.render(screen)

        CommonRender.RenderScore(screen, self.score)
        CommonRender.RenderHealth(screen, self.health)

        if self.paused:
            t_pause = gFonts['large'].render("PAUSED", False, (255, 255, 255))
            rect = t_pause.get_rect(center = (WIDTH/2, HEIGHT/2))
            screen.blit(t_pause, rect)


    def CheckVictory(self):
        for brick in self.bricks:
            if brick.alive or brick.unbreakable:
                return False

        return True
    
    def spawn_powerup(self, brick):
        offset = self.level * 0.01
        if random.random() < 0.4 + offset:  # 20% chance to spawn power-up
            power_up_type = random.choices(
                [PowerUpType.LASER_PADDLE, PowerUpType.EXTENDED_PADDLE, PowerUpType.BOMB_BALL],
                weights=[0.2, 0.5, 0.3]
            )[0]  
            power_up = PowerUp(brick.x, brick.y, power_up_type)
            self.power_ups.append(power_up)  # Add power-up to the active list

    def check_powerup_collision(self, paddle, power_up):
        """Check if the paddle collects the power-up."""
        if power_up.x + power_up.width < paddle.rect.x or power_up.x > paddle.rect.x + paddle.rect.width:
            return False
    
        if power_up.y + power_up.height < paddle.rect.y or power_up.y > paddle.rect.y + paddle.rect.height:
            return False
    
        self.activate_powerup(power_up)
        return True

    def activate_powerup(self, power_up):
        """Activates the power-up's effect."""
        if power_up.type == PowerUpType.LASER_PADDLE:
            self.activate_laser_paddle(power_up.x)
        elif power_up.type == PowerUpType.EXTENDED_PADDLE:
            self.activate_extended_paddle()
        elif power_up.type == PowerUpType.BOMB_BALL:
            self.activate_bomb_ball()

    def activate_laser_paddle(self, x):
        """Activate laser paddle effect for a limited time."""
        self.lasers.append(LaserBeam(x))

    def activate_extended_paddle(self):
        """Extend paddle size for a limited time."""
        if PowerUpType.EXTENDED_PADDLE not in self.power_up_timers:
            gSounds['powerup_paddle'].play()
            self.paddle.IncreasePadSize()
            self.paddle.start_blinking()
            self.power_up_timers[PowerUpType.EXTENDED_PADDLE] = POWERUP_TIMER
            
    def activate_bomb_ball(self):
        """Activate bomb ball effect."""
        gSounds['powerup_bomb'].play()  
        self.ball.StartBombBall()

    def deactivate_powerup(self, power_up_type):
        """Deactivate power-up effects when the timer runs out."""
        if power_up_type == PowerUpType.EXTENDED_PADDLE:
            self.paddle.DecreasePadSize()
            self.paddle.start_blinking()
        if power_up_type == PowerUpType.BOMB_BALL:
            self.ball.StopBombBall()
