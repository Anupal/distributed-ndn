# Component Descriptions

## Communication Flow
| Flow direction | Method | Notes |
| --- | --- |
| Sending Data (Node -> Socket) | direct call to self.conn.send | The comm layer will only send data. It is responsibility of higher layer to format the payload.
| Receiving Data (Socket -> Node ) | callbacks to the Node layer | Comm layer will check which component is required to process the packet and passes the packet to respective callback. For eg: Interest and Data packets go to handle_data and handle_interest callbacks in DataPlane while Hello packets will go to handle_hello callback in ControlPlane.|

## Table Structure
| Table | Structure |
| --- | --- |
| PIT | |
| FIB (neighbor_table) | <table><tr><th></th></tr></table> |
| | |

## Packet Structure

[PACKET_ID]~[PAYLOAD]

| Packet | Structure |
| --- | --- |
| Hello | "0|NODEID||IP|PORT|"  |

## 1. Node
Integrates Data plane and control layers while also interfacing with Cache and Sensor/Actuator core logic.

