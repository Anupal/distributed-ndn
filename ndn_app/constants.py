import random
from copy import copy


### GW
GW_NODE_LABEL = 9
GW_DETAILS = ("10.35.70.10", 33005, "/wristband/")
GW_KEY = "gateway.pem"

### NODES CORE
RPI1_IP = "10.35.70.38"
RPI2_IP = "10.35.70.16"
# RPI1_IP = "127.0.0.1"
# RPI2_IP = "127.0.0.1"

COORDINATE_SEED = 1  # 3
random.seed(COORDINATE_SEED)
GRID_DIMENSIONS = (1000, 1000)
NUM_NODES = 10

STARTING_SERVER_PORT = 33000
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

NODES = copy(NODES_1)
NODES.update(NODES_2)

### NEIGHBOR DISCOVERY ###
MINIMUM_NEIGHBORS = 3
HELLO_DELAY = 1
HELLO_TIMEOUT = 3
MAX_HELLO_COUNT = 5
MEMBER_KEY_PATH = "member.pem"

### PACKAGE STRUCTURE ###
HELLO_ID = 0
HELLO_ACK_ID = 4
DATA_ID = 1
INTEREST_ID = 2
