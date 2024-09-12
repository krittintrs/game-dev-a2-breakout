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

# MAX_COL = 13
# MAX_TIER = 3

class LevelMaker:
    def __init__(self):
        pass

    @classmethod
    def CreateMap(cls, level):
        bricks = []

        # Adjust parameters based on the stage (early, middle, late)
        if level <= 5:
            # Early Stage
            num_rows = random.randint(1, 3)
            num_cols = random.randint(5, 9)
            lowest_tier = 0
            highest_tier = 0   
            lowest_color = 1
            highest_color = 3 
        elif 6 <= level <= 10:
            # Middle Stage
            num_rows = random.randint(3, 5)
            num_cols = random.randint(7, 11)
            lowest_tier = 0
            highest_tier = random.randint(1, 2)  
            lowest_color = 2
            highest_color = 4
            # unbreakable_chance = 0.1  # 10% chance for unbreakable bricks
        else:
            # Late Stage
            num_rows = random.randint(5, 7)
            num_cols = random.randint(11, 13)
            lowest_tier = 2
            highest_tier = 3
            lowest_color = 3
            highest_color = 5
            # unbreakable_chance = 0.2  # 20% chance for unbreakable bricks

        for y in range(num_rows):
            skip_pattern = random.choice([True, False])
            alternate_pattern = random.choice([True, False])

            alternate_color1 = random.randint(lowest_color, highest_color)
            alternate_color2 = random.randint(lowest_color, highest_color)
            alternate_tier1 = random.randint(lowest_tier, highest_tier)
            alternate_tier2 = random.randint(lowest_tier, highest_tier)

            skip_flag = random.choice([True, False])

            alternate_flag = random.choice([True, False])

            solid_color = random.randint(1, highest_color)
            solid_tier = random.randint(0, highest_tier)

            for x in range(num_cols):
                if skip_pattern and skip_flag:
                    skip_flag = not skip_flag
                    continue
                else:
                    skip_flag = not skip_flag

                offset = (WIDTH - num_cols*BRICK_WIDTH)/2

                b = Brick(
                    x * BRICK_WIDTH + offset, 
                    y * BRICK_HEIGHT
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

        if len(bricks) == 0:
            return LevelMaker.CreateMap(level)

        else:
            return bricks