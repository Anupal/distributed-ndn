import os
from node import Node
import time
import constants
import multiprocessing
import sys
from prettytable import PrettyTable


def clear_screen():
    if os.name == "nt":
        os.system("cls")  # For Windows
    else:
        os.system("clear")


def show_help():
    table = PrettyTable()
    table.field_names = ["Command", "Description"]
    table.align["Command"] = "l"
    table.align["Description"] = "l"

    table.add_row(["help", "Show all commands"])
    table.add_row(["show all nodes", "Print all nodes on this Pi"])
    table.add_row(["show fib <node>", "Print Node neighbors"])
    table.add_row(["show pit <node>", "Print Node pending interests"])
    table.add_row(["show counters <node>", "Print Node packet Counters"])
    table.add_row(["send interest <node> <data-address>", "Send interest packet"])
    table.add_row(["show key member <node>", "Print member private key"])
    table.add_row(["show key gateway <node>", "Print member private key"])
    table.add_row(["show key priv <node>", "Print node public key"])
    table.add_row(["show key pub <node>", "Print node private key"])
    table.add_row(["show packets <node>", "Print last 10 packets"])
    table.add_row(["show knn <node>", "Print k-nearest"])
    table.add_row(["show state <node>", "Print current state of node"])
    table.add_row(["show gateway", "Print current state of node"])
    table.add_row(["pause <node>", "Pause node"])
    table.add_row(["unpause <node>", "Unpause node"])
    print("\nSUPPORTED COMMANDS\n")
    print(table, "\n")


def parse_input_prefix2(prefix, user_input, nodes):
    try:
        user_input = user_input.replace(prefix, "")
        label, data_address = user_input.split(" ")[:2]
        label = int(label)
        if label in nodes:
            return label, data_address
        else:
            print(f"Node {label} not found on this Pi!")
            return None, None
    except:
        print("Invalid input!")
        return None, None


def parse_input_prefix(prefix, user_input, nodes):
    try:
        label = int(user_input.replace(prefix, ""))
        if label in nodes:
            return label
        else:
            print(f"Node {label} not found on this Pi!")
    except:
        print("Invalid input!")


def loop(nodes):
    user_input = ""
    while user_input != "exit":
        sleep_duration = 1

        try:
            user_input = input("> ")

            if user_input == "clear":
                clear_screen()
                sleep_duration = 0

            if user_input == "help":
                show_help()
                sleep_duration = 0

            elif user_input == "show all nodes":
                print()
                for node in nodes:
                    print(node, end=" ")
                print()
                sleep_duration = 0

            elif user_input == "show gateway":
                if constants.GW_NODE_LABEL in nodes:
                    nodes[constants.GW_NODE_LABEL].mgmt.put(
                        {"call": "print_gateway", "args": ()}
                    )
                else:
                    print("Gateway is not running on this Pi!")

            elif "show fib " in user_input:
                label = parse_input_prefix("show fib ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_fib", "args": ()})

            elif "show pit " in user_input:
                label = parse_input_prefix("show pit ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_pit", "args": ()})

            elif "show knn " in user_input:
                label = parse_input_prefix("show knn ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_knn", "args": ()})

            elif "show counters " in user_input:
                label = parse_input_prefix("show counters ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_counters", "args": ()})

            elif "show packets " in user_input:
                label = parse_input_prefix("show packets ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_last_10", "args": ()})
                    sleep_duration = 1

            elif "show key member " in user_input:
                label = parse_input_prefix("show key member ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put(
                        {"call": "print_member_private_key", "args": ()}
                    )

            elif "show key gateway " in user_input:
                label = parse_input_prefix("show key gateway ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put(
                        {"call": "print_gateway_private_key", "args": ()}
                    )

            elif "show key priv " in user_input:
                label = parse_input_prefix("show key priv ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_private_key", "args": ()})

            elif "show key pub " in user_input:
                label = parse_input_prefix("show key pub ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_public_key", "args": ()})

            elif "unpause " in user_input:
                label = parse_input_prefix("unpause ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "start_comms", "args": ()})

            elif "pause " in user_input:
                label = parse_input_prefix("pause ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "stop_comms", "args": ()})

            elif "show state " in user_input:
                label = parse_input_prefix("show state ", user_input, nodes)
                if label != None:
                    nodes[label].mgmt.put({"call": "print_state", "args": ()})

            elif "send interest " in user_input:
                label, data_address = parse_input_prefix2(
                    "send interest ", user_input, nodes
                )
                if label != None:
                    nodes[label].mgmt.put(
                        {"call": "send_interest_packet", "args": (data_address, 1)}
                    )
                    sleep_duration = 2
            else:
                sleep_duration = 0

            time.sleep(sleep_duration)
        except KeyboardInterrupt:
            ...

    for node_id in nodes:
        nodes[node_id].terminate()
        nodes[node_id].join()


if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("Format: python3 main.py <rpi>")
        exit(1)

    rpi = int(args[1])

    if rpi == 1:
        start, end = 0, constants.NUM_NODES // 2
    elif rpi == 2:
        start, end = constants.NUM_NODES // 2, constants.NUM_NODES

    nodes = {}

    for i in range(start, end):
        mgmt = multiprocessing.Queue(maxsize=2)
        gw = True if i == constants.GW_NODE_LABEL else False

        node = Node(
            constants.NODES[i]["xy"][0],
            constants.NODES[i]["xy"][1],
            i,
            f"/data/{i}/",
            constants.NODES[i]["server_ip"],
            constants.NODES[i]["server_port"],
            constants.NODES,
            constants.MINIMUM_NEIGHBORS,
            constants.HELLO_DELAY,
            mgmt,
            constants.MEMBER_KEY_PATH,
            gw,
            constants.GW_KEY,
            constants.GW_DETAILS,
        )
        nodes[i] = node
        node.start()

    print("\nWelcome to Medical Sensor Network - NDN.\n")
    show_help()
    loop(nodes)
