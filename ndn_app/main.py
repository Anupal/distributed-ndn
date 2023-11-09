import sys
from node import Node
import time
import constants


def main():
    args = sys.argv

    if len(args) < 2:
        print("Format: python3 ndn_app/main.py <label>")
        exit(1)

    label = int(args[1])
    sport = constants.STARTING_SERVER_PORT + label

    print("ALL NODES: ", constants.NODES)

    print(f"STARTING NODE {label}")

    node = Node(
        label,
        "127.0.0.1",
        sport,
        constants.NODES,
        constants.MINIMUM_NEIGHBORS,
        constants.HELLO_DELAY,
    ).start()


if __name__ == "__main__":
    main()
