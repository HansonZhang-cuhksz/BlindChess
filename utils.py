import random

FAST_DELAY = 0.1
PAGE_REFRESH_DELAY = 0.5
SLOW_DELAY = 3.0

def get_pos_str(x, y):
    x = int(x)
    y = int(y)
    return "ABCDEFGHI"[y] + str(x)

def get_random_id(existing_ids=set()):
    new_id = random.randint(0, 0xFFFFFFFF)
    while new_id in existing_ids:
        new_id = random.randint(0, 0xFFFFFFFF)
    return new_id