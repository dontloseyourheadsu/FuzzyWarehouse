# Fuzzy Warehouse

A modular Python/Pygame simulation of warehouse operations, where robots use fuzzy logic to decide delivery zones for items based on their size, fragility, and priority.

---

## `dropzone.py`

**Defines**: `DropZone` class  
**Purpose**: Represents target areas where items are delivered.

### Key Components:
- Marks its position on the grid (`#`).
- Tracks how many items have been received (`items_received`).
- Renders itself as a blue square with an optional label.

---

## `fuzzy_logic.py`

Handles fuzzy classification of items into delivery zones.

### `ItemAttributes`:
- A simple container for `size`, `fragility`, and `priority` (all normalized in [0,1]).

### Membership Functions:

- **low(x)**:  
  - x ≤ 0.2: 1.0  
  - 0.2 < x ≤ 0.5: `(0.5 - x) / 0.3`  
  - x > 0.5: 0.0  

- **medium(x)**:  
  - x ≤ 0.2 or x ≥ 0.8: 0.0  
  - 0.2 < x < 0.5: `(x - 0.2) / 0.3`  
  - 0.5 ≤ x < 0.8: `(0.8 - x) / 0.3`  

- **high(x)**:  
  - x < 0.5: 0.0  
  - 0.5 ≤ x < 0.8: `(x - 0.5) / 0.3`  
  - x ≥ 0.8: 1.0  

---

### Rule Base (Using `min` for AND logic):

1. **Z1**: small & fragile & high priority  
   → `min(low(size), high(fragility), high(priority))`  
2. **Z2**: large & robust & high priority  
   → `min(high(size), low(fragility), high(priority))`  
3. **Z3**: fragile & medium priority  
   → `min(high(fragility), medium(priority))`  
4. **Z4**: large & robust & medium priority  
   → `min(high(size), low(fragility), medium(priority))`  
5. **Z5**: low priority  
   → `low(priority)` (no other conditions)

### Defuzzification:

- The zone with the highest rule activation is selected (winner-takes-all).

---

### Why Use Fuzzy Logic?

- Warehouse items vary continuously; crisp thresholds can misclassify borderline cases.
- Fuzzy sets (`low`, `medium`, `high`) allow gradual transitions and smoother decisions.

---

### Example Calculation

**Item Attributes**:
- Size = 0.3
- Fragility = 0.6
- Priority = 0.9

**Membership Degrees**:

| Attribute     | low(x)     | medium(x)   | high(x)     |
|---------------|------------|-------------|-------------|
| size = 0.3     | ≈ 0.667     | ≈ 0.333      | 0.0         |
| fragility = 0.6 | 0.0        | ≈ 0.667      | ≈ 0.333      |
| priority = 0.9  | 0.0        | 0.0          | 1.0         |

**Rule Activations**:

- **Z1** = `min(0.667, 0.333, 1.0)` = **0.333**
- **Z2** = `min(0.0, 0.0, 1.0)` = **0.0**
- **Z3** = `min(0.333, 0.0)` = **0.0**
- **Z4** = `min(0.0, 0.0, 0.333)` = **0.0**
- **Z5** = `low(priority)` = **0.0**

**Result**: Highest activation = **Z1**

---

## `item.py`

**Defines**: `Item` class  
**Purpose**: Represents an individual item with random attributes.

- Initializes `size`, `fragility`, and `priority` randomly in [0,1].
- Draws itself as a green circle on the grid.

---

## `itemgenerator.py`

**Defines**: `ItemGenerator` class  
**Purpose**: Spawns items at designated locations.

### Key Methods:
- `generate_item()`: Creates a new item with a 10% chance per cycle.
- `remove_item()`: Clears the item once picked up.
- Renders its cell as a black square.

---

## `main.py`

**Orchestrates the simulation**:

### Game Flow:
1. Generate new items.
2. Assign free robots to pick them up.
3. Use fuzzy logic to classify items into zones.
4. Move robots with pathfinding and collision avoidance.
5. Handle pickups and deliveries.
6. Render the grid, entities, and UI.

---

## `obstaclegenerator.py`

**Defines**: `ObstacleGenerator` class  
**Purpose**: Places obstacles (`.`) while preserving path connectivity.

### Key Features:
- Avoids placing obstacles adjacent to generators or dropzones.
- Uses BFS to validate connectivity.

---

## `robot.py`

**Defines**: `Robot` class

### States:
- `FREE`, `PICKUP`, `DELIVERING` (visualized with colored hats)

### Movement:
- BFS path planning.
- Collision avoidance using random detours and recovery strategies.

### Rendering:
- Draws the robot’s body, state hat, and direction eye.
