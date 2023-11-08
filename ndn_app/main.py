import sys
from node import SocketCommunication
import time


def main(label, sport, dport):
    conn = SocketCommunication(label, "127.0.0.1", sport)
    conn.listen()
    time.sleep(5)
    conn.send("127.0.0.1", dport, "Hello")


if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        print("Please pass Node ID and port as cmdline arg")

    print(f"STARTING NODE {args[1]}")
    main(args[1], int(args[2]), int(args[3]))
