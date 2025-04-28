# fuzzy_logic.py
import random

# Helper functions for fuzzy memberships
def low(x):
    return max(0.0, min(1.0, (0.5 - x) / 0.3)) if x <= 0.5 else 0.0

def medium(x):
    if 0.2 < x < 0.5:
        return (x - 0.2) / 0.3
    elif 0.5 <= x < 0.8:
        return (0.8 - x) / 0.3
    else:
        return 0.0

def high(x):
    return max(0.0, min(1.0, (x - 0.5) / 0.3)) if x >= 0.5 else 0.0

def classify_item(item):
    # Calculate membership degrees
    size_low = low(item.size)
    size_medium = medium(item.size)
    size_high = high(item.size)

    fragility_low = low(item.fragility)
    fragility_medium = medium(item.fragility)
    fragility_high = high(item.fragility)

    priority_low = low(item.priority)
    priority_medium = medium(item.priority)
    priority_high = high(item.priority)

    # Define firing strengths for each Zone rule
    rule_strengths = {
        'Z1': min(size_low, fragility_high, priority_high),   # Fast-Access Fragile
        'Z2': min(size_high, fragility_low, priority_high),   # Fast-Access Bulk
        'Z3': min(fragility_high, priority_medium),           # Climate-Controlled Fragile
        'Z4': min(size_high, fragility_low, priority_medium), # Bulk Storage
        'Z5': priority_low                                    # Long-Term / Overflow
    }

    # Choose the zone with the maximum firing strength
    best_zone = max(rule_strengths, key=rule_strengths.get)
    return best_zone
