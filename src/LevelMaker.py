import random, pygame, math
from src.Brick import Brick
from src.constants import *
from enum import Enum, auto

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

MAX_BRICK_STRENGTH = 19

class Pattern(Enum):
    DEFAULT = auto()
    ALT = auto()
    SKIP = auto()
    PYRAMID = auto()
    MULTIPLE = auto()

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

        global prev_rows, prev_cols, prev_brick_strength
        
        if level == STAGE1:
            num_rows = 1
            num_cols = 5
            
            selected_brick_strength = prev_brick_strength = 0
            selected_tier, selected_color = cls.derive_tier_and_color(selected_brick_strength)
            
            alt_strength, alt_tier, alt_color = selected_brick_strength, selected_tier, selected_color   

            pattern = Pattern.DEFAULT

        elif STAGE1 < level:
            # constraint
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

            # selected brick strength
            if level < STAGE3:
                selected_brick_strength = (level-1)//3
            else:
                inc_str = random.choices([0, 1], weights=[0.7, 0.3])[0]
                selected_brick_strength = min(prev_brick_strength + inc_str, MAX_BRICK_STRENGTH)
            selected_tier, selected_color = cls.derive_tier_and_color(selected_brick_strength)
            print(f'SELECTED STR: {selected_brick_strength} (T{selected_tier}-C{selected_color})')
            
            # default alternate & pattern
            alt_strength, alt_tier, alt_color = selected_brick_strength, selected_tier, selected_color
            pattern = Pattern.DEFAULT

            # if STR increased
            if selected_brick_strength > prev_brick_strength:
                print('??? STR UP ???')
                num_rows = min(max(prev_rows + random.randint(-1, 0), MIN_ROW), MAX_ROW)
                
                if num_rows < prev_rows:
                    # if row decrease, increase col
                    num_cols = min(prev_cols + 2, MAX_COL) 
                else: 
                    # if row the same, might increase col
                    inc_cols = random.choices([0, 2], weights=[0.3, 0.7])[0]
                    num_cols = min(max(prev_cols + inc_cols, MIN_COL), MAX_COL) 

                if random.choice([True, False]) and num_rows > 1:
                    pattern = Pattern.MULTIPLE
                else:
                    pattern = Pattern.PYRAMID
            # if STR the same
            else:
                if random.choice([True, False]):
                    # 1 - increase ROW, possibly decrease COL
                    print('??? SAME STR - ROW UP & COL MIGHT DOWN ???')
                    num_rows = min(prev_rows + 1, MAX_ROW)

                    dec_cols = random.choices([0, -2], weights=[0.3, 0.7])[0]
                    num_cols = min(max(prev_cols + dec_cols, MIN_COL), MAX_COL) 
                    
                    if random.choice([True, False]):
                        pattern = Pattern.SKIP
                    else:
                        pattern = Pattern.PYRAMID
                else:
                    # 1 - increase COL, sane ROW
                    print('??? SAME STR - COL UP & SAME ROW ???')
                    num_rows = max(prev_rows, MIN_ROW)
                    num_cols = min(max(prev_cols + 2, MIN_COL), MAX_COL) 
                    
                    inc_alt = random.choices([1, 2], weights=[0.7, 0.3])[0]
                    alt_strength = min(selected_brick_strength + inc_alt, MAX_BRICK_STRENGTH)
                    alt_tier, alt_color = cls.derive_tier_and_color(alt_strength)
                    pattern = Pattern.ALT

        # store previous value for next level
        prev_rows = num_rows
        prev_cols = num_cols
        prev_brick_strength = selected_brick_strength

        return num_rows, num_cols, selected_tier, selected_color, alt_tier, alt_color, pattern
    
    @classmethod
    def unbreakableGenerator(clf, level):
        if level < STAGE2:
            unbreakable = 0
        elif STAGE2 <= level < STAGE3:
            threshold = (level-STAGE2)*0.05
            unbreakable = random.choices([0, 1, 2], weights=[0.6 - threshold, 0.3 + threshold/2, 0.1 + threshold/2])[0]
        else:
            threshold = max((level-STAGE2)*0.01, 0.03)
            unbreakable = random.choices([2, 3, 4], weights=[0.3 - threshold/2, 0.3 - threshold/2, 0.4 + threshold])[0]
        
        return unbreakable

    @classmethod
    def CreateMap(clf, level):
        bricks = []
        
        num_rows, num_cols, selected_tier, selected_color, alt_tier, alt_color, pattern = clf.levelGenerator(level)
        unbreakable = clf.unbreakableGenerator(level)

        global prev_diff
        if level == 1:
            prev_diff = 0

        if num_rows < 4:
            y_offset = BRICK_HEIGHT * (4-num_rows)
        else:
            y_offset = 0

        # Alternate Pattern
        if pattern == Pattern.ALT: 
            alt_pattern_list = [1 for _ in range(num_rows)]
            alt_flags = clf.generate_flags(num_rows)
            if random.choice([True, False]) or num_rows > 3:
                pattern = Pattern.PYRAMID
        else:
            alt_pattern_list = [0 for _ in range(num_rows)]
            alt_flags = [0 for _ in range(num_rows)]

        # Skip Pattern
        if pattern == Pattern.SKIP:
            # ensure not skip more than 2-3 rows
            skip_pattern_list = [1 for _ in range(num_rows)]
            skip_count = skip_pattern_list.count(1)
            if num_rows < 4:
                skip_threshold = 3
            else:
                skip_threshold = 2
            while skip_count > skip_threshold:
                skip_indices = [i for i, val in enumerate(skip_pattern_list) if val == 1]
                index_to_convert = random.choice(skip_indices)
                skip_pattern_list[index_to_convert] = 0
                skip_count = skip_pattern_list.count(1)
            # generate skip flag for each row
            if num_rows == 1:
                skip_flags = [1]
            else:
                skip_flags = clf.generate_flags(num_rows)
        else: 
            skip_pattern_list = [0 for _ in range(num_rows)]
            skip_flags = [0 for _ in range(num_rows)]

        # Pyramid Pattern
        if pattern == Pattern.PYRAMID:
            choice = random.randint(1, 4)
            cols_list = []
            if choice == 1:     # single pyramid down
                cols_list = [max(num_cols - i, 1-(num_cols%2)) for i in range(num_rows)]
            elif choice == 2:   # single pyramid up
                cols_list = [max(num_cols - (num_rows-i-1), 1-(num_cols%2)) for i in range(num_rows)]
            elif choice == 3:   # double pyramid down-up (hourglass)
                middle = num_rows//2 + num_rows%2
                for i in range(num_rows):
                    if i < middle:
                        cols_list.append(max(num_cols - i*2, 2-(num_rows%2)))
                    else:
                        cols_list.append(max(num_cols - ((num_rows-middle)-(i-middle)-1)*2, 2-(num_rows%2)))
            elif choice == 4:   # double pyramid up-down
                middle = num_rows//2 + num_rows%2
                for i in range(num_rows):
                    if i < middle:
                        cols_list.append(max(num_cols - (middle-i-1)*2, 2-(num_rows%2)))
                    else:
                        cols_list.append(max(num_cols - (i-middle+num_rows%2)*2, 2-(num_rows%2)))
        else:
            cols_list = [num_cols for _ in range(num_rows)]

        # Multiple Pattern (Alternate & Skip)
        if pattern == Pattern.MULTIPLE:
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
        
        # Brick Construction
        num_bricks = 0
        difficulty = 0
        for y in range(num_rows):
            alt_pattern = alt_pattern_list[y]
            alt_flag = alt_flags[y]

            skip_pattern = skip_pattern_list[y]
            skip_flag = skip_flags[y]

            col = cols_list[y]

            bricks.append([])
            # if multiple_pattern:
            #     print(f'row: {y}')
            #     print(f'\twith ALTER {alt_pattern} ({alt_flag})')
            #     print(f'\twith SKIP  {skip_pattern} ({skip_flag})')

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

                bricks[y].append(b)
                num_bricks += 1
                difficulty += clf.calculate_brick_strength(b.tier, b.color) + 1
        
        # Debug
        print(f'LEVEL {level}')
        print(f'dimension: {num_rows} x {num_cols}')
        print(f'pattern: {pattern}')
        print(f'INITIAL: {prev_diff} + ({difficulty - prev_diff}) >>> {difficulty}')

        # Recursive Update
        row = 0
        brick_not_exceed = True
        while difficulty < prev_diff and brick_not_exceed:
            cur_diff = prev_diff - difficulty
            threshold = random.choices([1, 2], weights=[0.7, 0.3])[0]
            choice = random.randint(1, 3)
            print(f'>>> CMP: {cur_diff} / {threshold} @C{choice}')

            cols = len(bricks[row])
            for i, brick in enumerate(bricks[row]):
                if choice == 1 or cols <= 2:        # 1 - add whole row
                    increase = threshold
                elif choice == 2 and cols%2 == 1:   # 2.1 - odd alternate
                    if i%2 == 1:
                        increase = threshold*2
                    else:
                        increase = 0
                elif choice == 2 and cols%2 == 0:   # 2.2 - even alternate
                    if i in [0, cols//2-1, cols//2, cols-1]:
                        increase = threshold*2
                    else:
                        increase = 0
                elif choice == 3:                   # 3 - skip
                    break

                new_brick_strength  = clf.calculate_brick_strength(brick.tier, brick.color) + increase
                if new_brick_strength > MAX_BRICK_STRENGTH:
                    brick_not_exceed = False
                    break

                difficulty += increase

                brick.tier, brick.color = clf.derive_tier_and_color(new_brick_strength)
            
            row += 1
            if row == num_rows:
                row = 0
        
        print(f'!FINAL: {prev_diff} + ({difficulty - prev_diff}) >>> {difficulty}\n')

        # Unbreakable Feature
        if unbreakable > 0:
            print(f'unbreakable: {unbreakable}')
            chosen_row = random.randint(2, num_rows-1)
            choice = random.randint(0, 1)
            cols = len(bricks[chosen_row])
            middle = cols//2
            if unbreakable == 1:    # pattern unbreakable
                if choice:
                    if cols%2 == 1:
                        bricks[chosen_row][middle-1].Unbreaking()
                        bricks[chosen_row][middle].Unbreaking()
                        bricks[chosen_row][middle+1].Unbreaking()
                    else:
                        bricks[chosen_row][middle-1].Unbreaking()
                        bricks[chosen_row][middle].Unbreaking()
                else:
                    if cols%2 == 1:
                        bricks[chosen_row][middle-2].Unbreaking()
                        bricks[chosen_row][middle-1].Unbreaking()
                        bricks[chosen_row][middle+1].Unbreaking()
                        bricks[chosen_row][middle+2].Unbreaking()
                    else:
                        bricks[chosen_row][middle-2].Unbreaking()
                        bricks[chosen_row][middle-1].Unbreaking()
                        bricks[chosen_row][middle].Unbreaking()
                        bricks[chosen_row][middle+1].Unbreaking()
            elif unbreakable == 2:  # alternate unbreakable
                for i, brick in enumerate(bricks[chosen_row]):
                    if i%2 == choice:
                        brick.Unbreaking()
            elif unbreakable == 3:  # whole row unbreakable
                for i, brick in enumerate(bricks[chosen_row]):
                    if cols%2 == 1 and i not in [0, middle, cols-1]:
                        brick.Unbreaking()
                    elif cols%2 == 0 and i not in [0, middle-1, middle, cols-1]:
                        brick.Unbreaking()
            elif unbreakable == 4:  # outer unbreakable
                unbreak_pattern = [
                    [0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
                ]
                if num_rows <= 5:
                    outer_location = 8
                else:
                    outer_location = 9
                y_offset = outer_location*BRICK_HEIGHT
                unbreak_row_pattern = unbreak_pattern[random.randint(0, 3)]
                unbreak_row = []
                for x, place in enumerate(unbreak_row_pattern):
                    if not place:
                        continue
                    
                    x_offset = (WIDTH - 13*BRICK_WIDTH)/2

                    b = Brick(
                        x * BRICK_WIDTH + x_offset, 
                        y_offset
                    )

                    b.Unbreaking()

                    unbreak_row.append(b)
                bricks.append(unbreak_row)
        
        prev_diff = difficulty
        bricks = [brick for bricks_row in bricks for brick in bricks_row]

        if len(bricks) == 0:
            return LevelMaker.CreateMap(level)

        else:
            return bricks