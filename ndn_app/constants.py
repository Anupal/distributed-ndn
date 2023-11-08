import random

### NODES CORE
COORDINATE_SEED = 1
random.seed(COORDINATE_SEED)
GRID_DIMENSIONS = (1000, 1000)
NUM_NODES = 2
# Generate node coordinates by numeric ids
NODES = {
    i: (random.randint(0, GRID_DIMENSIONS + 1), random.randint(0, GRID_DIMENSIONS + 1))
    for i in range(NUM_NODES)
}

### NEIGHBOR DISCOVERY ###
MINIMUM_NEIGHBORS = 5
HELLO_DELAY = 1
HELLO_TIMEOUT = 3
