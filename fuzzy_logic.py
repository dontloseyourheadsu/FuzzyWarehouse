import random

class ItemAttributes:
    def __init__(self, size, fragility, priority):
        self.size = size
        self.fragility = fragility
        self.priority = priority

def low(x):
    return max(0.0, min(1.0, (0.5 - x) / 0.3)) if x <= 0.5 else 0.0

def medium(x):
    if 0.2 < x < 0.5:
        return (x - 0.2) / 0.3
    elif 0.5 <= x < 0.8:
        return (0.8 - x) / 0.3
    return 0.0

def high(x):
    return max(0.0, min(1.0, (x - 0.5) / 0.3)) if x >= 0.5 else 0.0

def classify_item(item_attr):
    sz, fr, pr = item_attr.size, item_attr.fragility, item_attr.priority

    s_low, s_med, s_high = low(sz), medium(sz), high(sz)
    f_low, f_med, f_high = low(fr), medium(fr), high(fr)
    p_low, p_med, p_high = low(pr), medium(pr), high(pr)

    rules = {
        'Z1': min(s_low,  f_high, p_high),
        'Z2': min(s_high, f_low,  p_high),
        'Z3': min(f_high, p_med),
        'Z4': min(s_high, f_low,  p_med),
        'Z5': p_low
    }
    return max(rules, key=rules.get)