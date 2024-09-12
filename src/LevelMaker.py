import random, pygame, math
from src.Brick import Brick
from src.constants import *

#patterns
NONE = 1
SINGLE_PYRAMID = 2
MULTI_PYRAMID = 3

SOLID = 1            # all colors the same in this row
ALTERNATE = 2        # alternative colors
SKIP = 3             # skip every other brick
NONE = 4             # no block this row

MAX_COL = 13

class LevelMaker:
    def __init__(self):
        pass

    @classmethod
    def CreateMap(cls, level):
        bricks = []

        # Not gooood enough!!
        num_rows = random.randint(1, 5)
        num_cols = random.randint(7, MAX_COL)
        if num_cols % 2 == 0:
            num_cols += 1
        highest_tier = min(3, math.floor(level/5.0))
        highest_color = min(5, level % 5 + 3)

        for y in range(num_rows):
            skip_pattern = random.choice([True, False])
            alternate_pattern = random.choice([True, False])

            alternate_color1 = random.randint(1, highest_color)
            alternate_color2 = random.randint(1, highest_color)
            alternate_tier1 = random.randint(0, highest_tier)
            alternate_tier2 = random.randint(0, highest_tier)

            skip_flag = random.choice([True, False])

            alternate_flag = random.choice([True, False])

            solid_color = random.randint(1, highest_color)
            solid_tier = random.randint(0, highest_tier)

            alternate_tier1, alternate_tier2, solid_tier = 3, 3, 3

            for x in range(num_cols):
                if skip_pattern and skip_flag:
                    skip_flag = not skip_flag
                    continue
                else:
                    skip_flag = not skip_flag

                b = Brick(
                    x*BRICK_WIDTH+24 + (MAX_COL-num_cols) * BRICK_HEIGHT, 
                    y*BRICK_HEIGHT
                )

                if alternate_pattern and alternate_flag:
                    b.color = alternate_color1
                    b.tier = alternate_tier1
                    alternate_flag = not alternate_flag
                else:
                    b.color = alternate_color2
                    b.tier = alternate_tier2
                    alternate_flag = not alternate_flag

                if not alternate_pattern:
                    b.color = solid_color
                    b.tier = solid_tier

                bricks.append(b)
            #table.insert(bricks, b)

        if len(bricks) == 0:
            return LevelMaker.CreateMap(level)

        else:
            return bricks