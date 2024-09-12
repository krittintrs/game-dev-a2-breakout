import pygame, math, os
from pygame import mixer
from src.constants import *


pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()

music_channel = mixer.Channel(0)
music_channel.set_volume(0.2)

from src.Dependency import *

# Credit for graphics:
# https://opengameart.org/users/buch
#
# Credit for music:
# http://freesound.org/people/joshuaempyre/sounds/251461/
# http://www.soundcloud.com/empyreanma


class GameMain:
    def __init__(self):
        self.max_frame_rate = 60
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.bg_image = pygame.image.load("./graphics/background.png")

        self.bg_image = pygame.transform.scale(
            self.bg_image, (WIDTH+5, HEIGHT+5))

        self.num_dup_images = math.ceil(WIDTH / self.bg_image.get_width()) + 1
        self.scroll = 0
        self.scroll_bg = False

        self.bg_music = pygame.mixer.Sound('sounds/music.wav')

        g_state_manager.SetScreen(self.screen)

        states = {
            'start': StartState(),
            'play': PlayState(),
            'serve': ServeState(),
            'game-over': GameOverState(),
            'victory': VictoryState(),
            'high-scores': HighScoreState(),
            'enter-high-score': EnterHighScoreState(),
            'paddle-select': PaddleSelectState()
        }
        g_state_manager.SetStates(states)

    def LoadHighScores(self):
        if not os.path.exists(RANK_FILE_NAME):
            with open(RANK_FILE_NAME, "w") as fp:
                for i in range(10, 0, -1):
                    scores = "AAA\n" + str(i*10) + "\n"
                    fp.write(scores)
                fp.close()

        file = open(RANK_FILE_NAME, "r+")
        all_lines = file.readlines()
        scores = []

        name_flip = True
        counter =0
        for i in range(10):
            scores.append({
                'name':'',
                'score':0
            })

        for line in all_lines:
            if name_flip:
                scores[counter]['name'] = line[:-1]
            else:
                scores[counter]['score'] = int(line[:-1])
                counter+=1

            name_flip = not name_flip

        return scores

    def RenderBackground(self):
        if self.scroll_bg:
            i = 0
            while i < self.num_dup_images:
                main.screen.blit(self.bg_image,
                                 (self.bg_image.get_width() * i + self.scroll, 0))  # appending same images to the back
                i += 1
            self.scroll -= 6
            if abs(self.scroll) > self.bg_image.get_width():
                self.scroll = 0
        else:
            main.screen.blit(self.bg_image, (0, 0))

    def RenderDebugImages(self):
        images_per_column = 4  # Number of images per column
        x_offset = 10  # Starting horizontal position
        y_offset = 10  # Starting vertical position
        column_width = 200  # Width of each column (adjust as needed)
        image_spacing = 10  # Space between images
        text_spacing = 5  # Space between image and text
        
        # Loop through images and render them in columns
        for i, image in enumerate(brick_image_list):
            # Blit the image
            self.screen.blit(image, (x_offset, y_offset))
            
            # Find the corresponding key for the image
            for key, value in sprite_collection.items():
                if value.image == image:
                    text = gFonts["small"].render(key, True, (255, 255, 255))  # White text
                    self.screen.blit(text, (x_offset, y_offset + image.get_height() + text_spacing))
                    break
            
            # Update vertical offset for the next image
            y_offset += image.get_height() + image_spacing + gFonts["small"].get_height() + text_spacing
            
            # Move to the next column after `images_per_column` images
            if (i + 1) % images_per_column == 0:
                x_offset += column_width
                y_offset = 10  # Reset y_offset for the new column

            # Adjust the position if you need more space or have different column widths
            if x_offset + column_width > WIDTH:
                x_offset = 10
                y_offset += max(image.get_height() + gFonts["small"].get_height() + text_spacing, 500)  # Adjust as needed
    

    def PlayGame(self):
        self.bg_music.play(-1)
        clock = pygame.time.Clock()
        g_state_manager.Change('start', {
            'high_scores': self.LoadHighScores(),
        })

        while True:
            pygame.display.set_caption("breakout game running with {:d} FPS".format(int(clock.get_fps())))
            dt = clock.tick(self.max_frame_rate) / 1000.0

            #input
            events = pygame.event.get()

            #update
            g_state_manager.update(dt, events)

            #bg render
            self.RenderBackground()

            # Render debug images and names
            self.RenderDebugImages()

            #render
            # g_state_manager.render()

            #screen update
            pygame.display.update()


if __name__ == '__main__':
    main = GameMain()

    main.PlayGame()



