import random

### NODES CORE
RPI1_IP = "127.0.0.1"
RPI2_IP = "127.0.0.1"

COORDINATE_SEED = 1
random.seed(COORDINATE_SEED)
GRID_DIMENSIONS = (1000, 1000)
NUM_NODES = 2

STARTING_SERVER_PORT = 34000
STARTING_CLIENT_PORT = 35000

# Generate node coordinates by numeric ids
NODES_1 = {
    i: {
        "server_ip": RPI1_IP,
        "server_port": STARTING_SERVER_PORT + i,
        "client_port": STARTING_CLIENT_PORT + i,
        "xy": (
            random.randint(0, GRID_DIMENSIONS[0] + 1),
            random.randint(0, GRID_DIMENSIONS[1] + 1),
        ),
    }
    for i in range(0, NUM_NODES // 2)
}

NODES_2 = {
    i: {
        "server_ip": RPI2_IP,
        "server_port": STARTING_SERVER_PORT + i,
        "client_port": STARTING_CLIENT_PORT + i,
        "xy": (
            random.randint(0, GRID_DIMENSIONS[0] + 1),
            random.randint(0, GRID_DIMENSIONS[1] + 1),
        ),
    }
    for i in range(NUM_NODES // 2, NUM_NODES)
}

NODES = NODES_1 | NODES_2

### NEIGHBOR DISCOVERY ###
MINIMUM_NEIGHBORS = 5
HELLO_DELAY = 1
HELLO_TIMEOUT = 3
