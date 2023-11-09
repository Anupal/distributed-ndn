# Component Descriptions

## Communication Flow
| Flow direction | Method | Notes |
| --- | --- | --- |
| Sending Data (Node -> Socket) | direct call to self.conn.send | The comm layer will only send data. It is responsibility of higher layer to format the payload.
| Receiving Data (Socket -> Node ) | callbacks to the Node layer | Comm layer will check which component is required to process the packet and passes the packet to respective callback. For eg: Interest and Data packets go to handle_data and handle_interest callbacks in DataPlane while Hello packets will go to handle_hello callback in ControlPlane.|

## Table Structure
All can be be represented as dictionaries with first column as the key.

### FIB (neighbor_table)
<table>
    <thead><tr>
        <td>Neighbor Label</td>
        <td>TCP IP</td>
        <td>TCP Port</td>
        <td>Hello Count</td>
        <td>Certificate</td>
    </tr></thead>
</table>

### PIT (Pending Interest Table)
<table>
    <thead><tr>
        <td>(Data address, Neighbor Label)</td>
        <td>Index</td>
    </tr></thead>
</table>

### Cache
<table>
    <thead><tr>
        <td>Data address</td>
        <td>Data</td>
    </tr></thead>
</table>

## Packet Structure

[PACKET_ID]~[PAYLOAD]

| Packet | Structure |
| --- | --- |
| Hello | "0|NEIGHBOR_LABEL|IP|PORT|CERT"  |
| Data | "1|DATA ADDRESS|DATA|SIGN"  |
| Interest | "2|DATA ADDRESS|NEIGHBOR_LABEL|Index|SIGN" |

## Components
### 1. SocketCommunication
1. **Server:**
    * Listens on a separate thread for incoming TCP sessions.
    * When a packet comes, check the type (0, 1, 2) and execute the respective callback.
2. **Client:**
    * Sends packet to destination based on IP and port. The payload has to be preformatted in higher layers.

### 2. Node
Integrates Data plane and control layers while also interfacing with Cache and Sensor/Actuator core logic.

Architecture is callback driven. The callbacks are registered in Comm object and are called when a their associated packet is received.

#### handle_hello
1. Use crypto object to verify certificate
2. Parse Neighbor Label, IP, Port and Certificate.
3. If Neighbor Label is in FIB
    * increment Hello Count (till max value as specified in constants file)
4. If Neighbor Label is not in FIB
    * add new entry with count 1
5. This will establish neighborship.

#### handle_data
1. Use crypto object to verify signature
2. Parse Data address and Data
3. For entries in PIT that match data address
    * Send data
    * Remove PIT entry

#### handle_interest
1. Use crypto object to verify signature
2. Parse data address, neighbor label and index.
3. If (data address, neighbor label) exists in PIT:
    * If received packet index <= table index, drop packet as it is a duplicate and can cause network loop
    * If received packet index > table index, change packet index and forward to all nodes in FIB. (packet is a retry)
4. If (data address, neighbor label) not in PIT:
    * Add new entry, and forward to all neighbors