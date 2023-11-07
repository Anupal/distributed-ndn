# distributed-ndn

### Node hello processes
* Nodes running as processes
* Each node has a UDP server thread which listens for incoming packets and a main thread which sends hello to all peers

### Graph simulation
* 1000x1000 grid space where each node will have a random physical coordinate
* 20 nodes
* Every node will form links with 5 nearest neighbors
* Balancing NUM_NODES and CONNECTIVITY (k) will give a graph which will be connected even when some nodes die.


### How to run graph simulation
1. Install packages
```
pip install -r requirements.txt
```
2. Execute main.py
```
cd simulations && python3 main.py

```


### Network Layer (Theoretical)
1. Simulate wireless network using dynamic node positions
    * a central coordinate for every group
    * nodes running in group get coordinates within the defined radius of the group
    * neighbor discovery: every node listens for neighbors: calculate received signal strength as a function of euclidean distance and noise
    * A common file for all node to figure out its coordinates and neighbors
2. All communication using UDP packets
3. Advertisements to all nearby nodes.
    * Content
        * Data information
        * Current timestamp
        * Proof of identity signed data + timestamp
        * public key
    * When received and verified, node registers as a neighbor and adds to neighbor table as a link
    * Node has an advertisement period
    * If neighbor fails to send 3 times (dampening), then it is removed from table
4. Node:
    * Neighbor table -> FIB
    * Cache -> Content Store
    * Pending Interest Table -> PIT
5. Node - either sensor or collecter
6. Longest prefix match
