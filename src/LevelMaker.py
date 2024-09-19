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

    def levelGenerator(level):
        # Constraints

        STAGE1 = 1
        STAGE1_MIN_ROW = 1
        STAGE1_MAX_ROW = 3
        STAGE1_MIN_COL = 5
        STAGE1_MAX_COL = 9

        STAGE2 = 7
        STAGE2_MIN_ROW = 2
        STAGE2_MAX_ROW = 5
        STAGE2_MIN_COL = 7
        STAGE2_MAX_COL = 11

        STAGE3 = 12

        global previous_rows, previous_cols, previous_brick_strength, isPrevSTRUP, isPrevSameSTR
        
        if level == STAGE1:
            num_rows = 1
            num_cols = 5
            selected_brick_strength = previous_brick_strength = 0
            selected_tier, selected_color = derive_tier_and_color(selected_brick_strength)
            
            alternate_strength, alternate_tier, alternate_color = selected_brick_strength, selected_tier, selected_color   
            alternate_pattern = False
            skip_pattern = False
            
            increment = 0
            
            isPrevSTRUP = False
            isPrevSameSTR = True

        elif STAGE1 < level < STAGE3:
            if STAGE1 < level < STAGE2:
                MIN_ROW = STAGE1_MIN_ROW
                MAX_ROW = STAGE1_MAX_ROW
                MIN_COL = STAGE1_MIN_COL
                MAX_COL = STAGE1_MAX_COL
            elif STAGE2 <= level < STAGE3:
                MIN_ROW = STAGE2_MIN_ROW
                MAX_ROW = STAGE2_MAX_ROW
                MIN_COL = STAGE2_MIN_COL
                MAX_COL = STAGE2_MAX_COL

            selected_brick_strength = (level-1)//2
            selected_tier, selected_color = derive_tier_and_color(selected_brick_strength)
            
            alternate_strength, alternate_tier, alternate_color = selected_brick_strength, selected_tier, selected_color
                
            alternate_pattern = False
            skip_pattern = False

            if selected_brick_strength > previous_brick_strength and not isPrevSTRUP:
                print('>>> STR UP <<<<')
                num_rows = min(max(previous_rows + get_increment(level)*-1, MIN_ROW), MAX_ROW)
                num_cols = min(max(previous_cols + get_increment(level)*2, MIN_COL), MAX_COL) 
                isPrevSTRUP = True
                isPrevSameSTR = False
            else:
                print('>>> SAME STR - ROW UP <<<<')
                num_rows = min(previous_rows + 1, MAX_ROW)
                num_cols = min(max(previous_cols, MIN_COL), MAX_COL) 
                isPrevSTRUP = False
                
                if not isPrevSameSTR:
                    isPrevSameSTR = True
                    alternate_strength = selected_brick_strength + 1
                    alternate_tier, alternate_color = derive_tier_and_color(alternate_strength)
                    alternate_pattern = True
                else:
                    num_cols = min(max(previous_cols + get_increment(level)*2, MIN_COL), STAGE1_MAX_COL) 
                    skip_pattern = True
                    
        # Calculate the number of bricks
        num_bricks = num_rows * num_cols
        
        # Constructing the strength based on color and tier
        brick_strength = calculate_brick_strength(selected_tier, selected_color)
        
        # Calculate difficulty as a function of brick strength and the number of bricks
        difficulty = brick_strength * num_bricks

        print(f'LEVEL {level}')
        print(f'dimension: {num_rows} x {num_cols} ({num_bricks})')
        # print(f'STR: {previous_brick_strength} + {increment}')
        print(f'SELECTION >>> STR: {selected_brick_strength} (T{selected_tier}-C{selected_color})')
        print(f'\twith ALTER {alternate_pattern} {alternate_strength}')
        print(f'\twith SKIP  {skip_pattern}')
        print(f'Difficulty: {difficulty}\n')

        previous_rows = num_rows
        previous_cols = num_cols
        previous_brick_strength = brick_strength

        return num_rows, num_cols, selected_tier, selected_color, alternate_pattern, alternate_tier, alternate_color, skip_pattern

    @classmethod
    def CreateMap(cls, level):
        bricks = []
        
        num_rows, num_cols, selected_tier, selected_color, alternate_pattern, alternate_tier, alternate_color, skip_pattern = cls.levelGenerator(level)

        for y in range(num_rows):

            skip_flag = random.choice([True, False])
            alternate_flag = random.choice([True, False])

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
                    b.color = alternate_color
                    b.tier = alternate_tier
                    alternate_flag = not alternate_flag
                else:
                    b.color = selected_color
                    b.tier = selected_tier
                    alternate_flag = not alternate_flag

                if not alternate_pattern:
                    b.color = selected_color
                    b.tier = selected_tier

                bricks.append(b)

        if len(bricks) == 0:
            return LevelMaker.CreateMap(level)

        else:
            return bricks
        
# Define brick hitpoints based on color and tier
def calculate_brick_strength(tier, color):
    return tier * 5 + color  # Tier has more impact than color

def derive_tier_and_color(strength):
    tier = strength // 5
    color = (strength % 5)
    return tier, color

def get_increment(level, initial_one_prob=0.3, increment=0.05, max_prob=0.9):
    # Calculate the probability of getting 1 based on the level
    current_one_prob = min(initial_one_prob + increment * (level - 1), max_prob)
    if level == 1: return 0
    return 1 if random.random() < current_one_prob else 0
