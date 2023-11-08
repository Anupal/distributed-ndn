import sys
from node import SocketCommunication
import time


def main():
    args = sys.argv

    if len(args) < 4:
        print("Format: python3 tests/comm.py <label> <sport> <dport>")
        exit(1)

    label, sport, dport = (*args[1:],)

    print(f"STARTING NODE {label}")

    conn = SocketCommunication(label, "127.0.0.1", int(sport))
    conn.listen()
    time.sleep(5)
    conn.send("127.0.0.1", int(dport), "Hello")


if __name__ == "__main__":
    main()
