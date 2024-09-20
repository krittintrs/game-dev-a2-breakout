import random, pygame, math
from src.Brick import Brick
from src.constants import *

#patterns
NONE = 1
SINGLE_PYRAMID = 2
MULTI_PYRAMID = 3

SOLID = 1            # all colors the same in this row
alt = 2        # alternative colors
SKIP = 3             # skip every other brick
NONE = 4             # no block this row

# MAX_COL = 13
# MAX_TIER = 3

class LevelMaker:
    def __init__(self):
        pass

    @classmethod
    def calculate_brick_strength(cls, tier, color):
        return tier * 5 + color  # Tier has more impact than color

    @classmethod
    def derive_tier_and_color(cls, strength):
        tier = strength // 5
        color = (strength % 5)
        return tier, color

    @classmethod
    def get_increment(cls, level, initial_probs=(0.7, 0.3), increment=0.05, max_prob=0.9):
        # Unpack initial probabilities
        prob_0, prob_1 = initial_probs
        
        if level > 8:
            level -= 8
        # Increase the probability of getting 1 with the level, but cap it at max_prob
        prob_1 = min(prob_1 + increment * level, max_prob)
        prob_0 = 1 - prob_1  # Ensure the total probability sums to 1

        if level == 1: return 0
        # Generate a random choice based on the updated probabilities
        choice = random.choices([0, 1], weights=[prob_0, prob_1])[0]
        return choice
    
    @classmethod
    def generate_flags(cls, num_rows):
        flags = []
        
        if num_rows % 2 == 1:  # Odd case: alternate between 0 and 1
            flags = [i % 2 for i in range(num_rows)]
            if random.choice([True, False]):
                flags = [1 - x for x in flags]  # Randomize starting with 0 or 1
        
        else:  # Even case: alternate or repeat once before alternating
            if random.choice([True, False]):
                flags = [i % 2 for i in range(num_rows)]  # Regular alternating
            else:
                flags = [(i+1)//2 % 2 for i in range(num_rows)]  # Repeating once then alternate
            if random.choice([True, False]):
                flags = [1 - x for x in flags]  # Randomize starting with 0 or 1

        return flags

    @classmethod
    def levelGenerator(cls, level):
        # Constraints

        STAGE1 = 1
        STAGE1_MIN_ROW = 1
        STAGE1_MAX_ROW = 3
        STAGE1_MIN_COL = 5
        STAGE1_MAX_COL = 9

        STAGE2 = 7
        STAGE2_MIN_ROW = 3
        STAGE2_MAX_ROW = 5
        STAGE2_MIN_COL = 7
        STAGE2_MAX_COL = 11

        STAGE3 = 16
        STAGE3_MIN_ROW = 4
        STAGE3_MAX_ROW = 7
        STAGE3_MIN_COL = 9
        STAGE3_MAX_COL = 13

        global prev_rows, prev_cols, prev_brick_strength
        
        if level == STAGE1:
            num_rows = 1
            num_cols = 5
            selected_brick_strength = prev_brick_strength = 0
            selected_tier, selected_color = cls.derive_tier_and_color(selected_brick_strength)
            
            alt_strength, alt_tier, alt_color = selected_brick_strength, selected_tier, selected_color   
            alt_pattern = False
            skip_pattern = False
            pyramid_pattern = False
            multiple_pattern = False

        elif STAGE1 < level:# < STAGE3:
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
            else:
                MIN_ROW = STAGE3_MIN_ROW
                MAX_ROW = STAGE3_MAX_ROW
                MIN_COL = STAGE3_MIN_COL
                MAX_COL = STAGE3_MAX_COL

            selected_brick_strength = (level-1)//3
            selected_tier, selected_color = cls.derive_tier_and_color(selected_brick_strength)
            
            alt_strength, alt_tier, alt_color = selected_brick_strength, selected_tier, selected_color
            alt_pattern = False
            skip_pattern = False
            pyramid_pattern = False
            multiple_pattern = False

            if selected_brick_strength > prev_brick_strength:
                print('>>> STR UP <<<<')
                num_rows = min(max(prev_rows + cls.get_increment(level)*-1, MIN_ROW), MAX_ROW)
                
                if num_rows < prev_rows:
                    num_cols = min(prev_cols + 2, MAX_COL) 
                else: 
                    num_cols = min(max(prev_cols + cls.get_increment(level)*2, MIN_COL), MAX_COL) 

                if random.choice([True, False]) and num_rows > 1:
                    multiple_pattern = True
                else:
                    pyramid_pattern = True

            else:
                if random.choice([True, False]):
                    print('>>> SAME STR - ROW UP & SKIP <<<<')
                    num_rows = min(prev_rows + 1, MAX_ROW)
                    num_cols = min(max(prev_cols + cls.get_increment(level)*-2, MIN_COL), MAX_COL) 
                    
                    if random.choice([True, False]):
                        skip_pattern = True
                    else:
                        pyramid_pattern = True
                else:
                    print('>>> SAME STR - COL UP & ALTER <<<<')
                    num_rows = max(prev_rows, MIN_ROW)
                    num_cols = min(max(prev_cols + 2, MIN_COL), MAX_COL) 
                    
                    alt_strength = selected_brick_strength + 1
                    alt_tier, alt_color = cls.derive_tier_and_color(alt_strength)
                    alt_pattern = True

                    if random.choice([True, False]):
                        pyramid_pattern = True

        prev_rows = num_rows
        prev_cols = num_cols
        prev_brick_strength = selected_brick_strength

        return num_rows, num_cols, selected_tier, selected_color, alt_pattern, alt_tier, alt_color, skip_pattern, pyramid_pattern, multiple_pattern
    
    @classmethod
    def CreateMap(clf, level):
        bricks = []
        
        num_rows, num_cols, selected_tier, selected_color, alt_pattern, alt_tier, alt_color, skip_pattern, pyramid_pattern, multiple_pattern = clf.levelGenerator(level)

        if num_rows < 4:
            y_offset = BRICK_HEIGHT*(4 - num_rows)
        else:
            y_offset = 0

        if alt_pattern: 
            alt_pattern_list = [1 for _ in range(num_rows)]
            alt_flags = clf.generate_flags(num_rows)
            print(f'alter_flags: {alt_flags}')
        else:
            alt_pattern_list = [0 for _ in range(num_rows)]
            alt_flags = [0 for _ in range(num_rows)]

        if skip_pattern: 
            skip_pattern_list = [1 for _ in range(num_rows)]
            if num_rows == 1:
                skip_flags = [1]
            else:
                skip_flags = clf.generate_flags(num_rows)
            
            skip_count = skip_pattern_list.count(1)
            while skip_count > 3:
                skip_indices = [i for i, val in enumerate(skip_pattern_list) if val == 1]
                
                index_to_convert = random.choice(skip_indices)
                skip_pattern_list[index_to_convert] = 0
                
                skip_count = skip_pattern_list.count(1)

        else: 
            skip_pattern_list = [0 for _ in range(num_rows)]
            skip_flags = [0 for _ in range(num_rows)]

        if pyramid_pattern:
            choice = random.randint(1, 4)
            cols_list = []
            if choice == 1:     # single pyramid down
                print('single reverse pyramid')
                cols_list = [max(num_cols - i*2, 2-(num_rows%2)) for i in range(num_rows)]
            elif choice == 2:   # single pyramid up
                print('single pyramid')
                cols_list = [max(num_cols - (num_rows-i-1)*2, 2-(num_rows%2)) for i in range(num_rows)]
            elif choice == 3:   # double pyramid down-up (hourglass)
                print('double pyramid down-up (hourglass)')
                middle = num_rows//2 + num_rows%2
                print(f'middle: {middle}')
                for i in range(num_rows):
                    print(i)
                    if i < middle:
                        cols_list.append(max(num_cols - i*2, 2-(num_rows%2)))
                        print(f'D-col {i}: {num_cols - i*2} VS {2-(num_rows%2)} / {cols_list}')
                    else:
                        cols_list.append(max(num_cols - ((num_rows-middle)-(i-middle)-1)*2, 2-(num_rows%2)))
                        print(f'U-col {i}: {num_cols - ((num_rows-middle)-(i-middle)-1)*2} VS {2-(num_rows%2)} / {cols_list}')
                print(cols_list)
            elif choice == 4:   # double pyramid up-down
                print('double pyramid up-down')
                middle = num_rows//2 + num_rows%2
                for i in range(num_rows):
                    print(i)
                    if i < middle:
                        cols_list.append(max(num_cols - (middle-i-1)*2, 2-(num_rows%2)))
                        print(f'U-col {i}: {num_cols - (middle-i-1)*2} VS {2-(num_rows%2)} / {cols_list}')
                    else:
                        cols_list.append(max(num_cols - (i-middle+num_rows%2)*2, 2-(num_rows%2)))
                        print(f'D-col {i}: {num_cols - (i-middle+num_rows%2)*2} VS {2-(num_rows%2)} / {cols_list}')
                print(cols_list)
        else:
            cols_list = [num_cols for _ in range(num_rows)]

        if multiple_pattern:
            for i in range(num_rows):
                skip = random.choice([True, False])
                if skip:
                    skip_pattern_list[i] = 1
                    alt_pattern_list[i] = 0
                else:
                    skip_pattern_list[i] = 0
                    if random.choice([True, False]):
                        alt_pattern_list[i] = 1
                    else:
                        alt_pattern_list[i] = 0
            print('----MULTI')
            print(f'skip_flags: {skip_flags}')
            print(f'skip_pattern_list: {skip_pattern_list}')
            print(f'alt_flags: {alt_flags}')
            print(f'alt_pattern_list: {alt_pattern_list}')
        
        # for debugging
        num_bricks = 0
        difficulty = 0
        print(f'LEVEL {level}')
        print(f'SELECTION >>> STR: {clf.calculate_brick_strength(selected_tier, selected_color)} (T{selected_tier}-C{selected_color})')
        print(f'\twith ALTER {alt_pattern}')
        print(f'\twith SKIP  {skip_pattern}')
        print(f'\twith PYRA  {pyramid_pattern}')
        print(f'\twith MULTI {multiple_pattern}')

        for y in range(num_rows):
            alt_pattern = alt_pattern_list[y]
            alt_flag = alt_flags[y]

            skip_pattern = skip_pattern_list[y]
            skip_flag = skip_flags[y]

            col = cols_list[y]

            if multiple_pattern:
                print(f'row: {y}')
                print(f'\twith ALTER {alt_pattern} ({alt_flag})')
                print(f'\twith SKIP  {skip_pattern} ({skip_flag})')

            for x in range(col):
                if skip_pattern and skip_flag:
                    skip_flag = not skip_flag
                    continue
                else:
                    skip_flag = not skip_flag

                x_offset = (WIDTH - col*BRICK_WIDTH)/2

                b = Brick(
                    x * BRICK_WIDTH + x_offset, 
                    y * BRICK_HEIGHT + y_offset
                )

                if alt_pattern and alt_flag:
                    b.color = alt_color
                    b.tier = alt_tier
                    alt_flag = not alt_flag
                else:
                    b.color = selected_color
                    b.tier = selected_tier
                    alt_flag = not alt_flag

                if not alt_pattern:
                    b.color = selected_color
                    b.tier = selected_tier

                bricks.append(b)
                num_bricks += 1
                difficulty += clf.calculate_brick_strength(b.tier, b.color)
        
        print(f'dimension: {num_rows} x {num_cols}')
        print(f'Difficulty: {difficulty} >>> ({num_bricks})\n')

        if len(bricks) == 0:
            return LevelMaker.CreateMap(level)

        else:
            return bricks