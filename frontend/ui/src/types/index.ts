export interface Comm {
    server_ip: string,
    server_port: number
}

export interface InPackageCounters {
    hello: number,
    hello_ack: number,
    interest: number,
    data: number
}

export interface OutPackageCounters {
    hello: number,
    hello_ack: number,
    interest_org: number,
    interest_fwd: number,
    data_org: number,
    data_fwd: number,
}

export interface PacketCounters {
    in: InPackageCounters,
    out: OutPackageCounters
}

export interface FibEntry {
    label: number,
    hello_count: number
}

export interface PitEntry {
    data_address: string,
    retry_index: number,
    request_id: string
    label: string
}

export interface NDN {
    fib: FibEntry[],
    pit: PitEntry[]
}

export interface GwNode{
    is_node_marked: boolean,
    peer_connection: [string, number]
}

export interface NodeState {
    x: number,
    y: number,
    comms_enabled: boolean
    comm: Comm,
    gw_node: GwNode,
    packet_counters: PacketCounters,
    last_10_packets: string[],
    data_address: string,
    label: number,
    ndn: NDN,
}
