import sys
from node import Node
import time
import constants
import multiprocessing


def display_menu():
    print("\nWelcome to NDN text console. Please choose an option")
    print("-----------------------------\n")
    print("----- DISPLAY COMMANDS ------")
    print("0. Display menu")
    print("1. Print all nodes on this Pi")
    print("2. Print Node FIB")
    print("3. Print Node PIT")
    print("4. Print Node packet counters")
    print("\n--- INTERACTION COMMANDS ----")
    print("5. Send interest packet")
    print("\n----- SECURITY COMMANDS -----")
    print("6. Print certificate")
    print("7. Print public key")
    print("8. Print private key")
    print("\n------ DEBUG COMMANDS -------")
    print("9. Print last 10 packets")
    print("10. Print k-nearest")
    print("\n-----------------------------")
    print("Note: Give -1 as an option to exit from any menu.\n")


def display_all_nodes(nodes):
    print("Running nodes: ", end="")
    for node in nodes:
        print(node, end=", ")
    print()


def display_fib(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return
    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_fib", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def display_pit(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return

    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_pit", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def display_knn(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return

    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_knn", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def display_counters(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return

    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_counters", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def display_last_10(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return

    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_last_10", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def display_private_key(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return

    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_private_key", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def display_public_key(nodes):
    index = input("Enter node index: ")
    if "-1" == index:
        return

    index = int(index)
    if index in nodes:
        nodes[index].mgmt.put({"call": "print_public_key", "args": ()})
    else:
        print(f"Node {index} not found on this Pi!")


def send_interest_packet(nodes):
    index = input("Enter node index: ")
    data_address = input("Enter data address: ")
    retry = input("Enter retry index: ")
    if "-1" in (index, retry):
        return
    index, retry = int(index), int(retry)
    nodes[index].mgmt.put(
        {"call": "send_interest_packet", "args": (data_address, retry)}
    )


def main():
    args = sys.argv

    if len(args) < 2:
        print("Format: python3 ndn_app/main.py <rpi>")
        exit(1)

    rpi = int(args[1])

    if rpi == 1:
        start, end = 0, constants.NUM_NODES // 2
    elif rpi == 2:
        start, end = constants.NUM_NODES // 2, constants.NUM_NODES

    nodes = {}

    for i in range(start, end):
        print(f"Starting node {i}", flush=True)

        mgmt = multiprocessing.Queue(maxsize=2)

        node = Node(
            constants.NODES[i]["xy"][0],
            constants.NODES[i]["xy"][1],
            i,
            f"/data/{i}",
            constants.NODES[i]["server_ip"],
            constants.NODES[i]["server_port"],
            constants.NODES,
            constants.MINIMUM_NEIGHBORS,
            constants.HELLO_DELAY,
            mgmt,
            constants.MEMBER_KEY_PATH,
        )
        nodes[i] = node
        node.start()

    # Start menu loop

    display_menu()
    while True:
        sleep_duration = 2
        choice = input("> ")

        if choice == "0":
            display_menu()
            sleep_duration = 0
        elif choice == "1":
            display_all_nodes(nodes)
            sleep_duration = 0
        elif choice == "2":
            display_fib(nodes)
        elif choice == "3":
            display_pit(nodes)
        elif choice == "4":
            display_counters(nodes)
        elif choice == "5":
            send_interest_packet(nodes)
        elif choice == "7":
            display_public_key(nodes)
        elif choice == "8":
            display_private_key(nodes)
        elif choice == "9":
            display_last_10(nodes)
        elif choice == "10":
            display_knn(nodes)
        elif choice == "-1":
            for node_id in nodes:
                nodes[node_id].terminate()
                nodes[node_id].join()
            exit()
        else:
            sleep_duration = 0

        time.sleep(sleep_duration)


if __name__ == "__main__":
    main()
