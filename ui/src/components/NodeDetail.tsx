import React from "react";
import {NodeState} from "../types";
import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow} from "@mui/material";
import Typography from "@mui/material/Typography";
import {hashCode} from "../util/hashing";

interface NodeDetailProps {
    selectedNodeState: NodeState
}

export const NodeDetail = ({selectedNodeState}: NodeDetailProps) => {
    const element = <>
        <Typography variant="h6" gutterBottom align='center'>
            PIT
        </Typography>
        <TableContainer component={Paper}>
            <Table sx={{minWidth: "100%"}}>
                <TableHead>
                    <TableCell>Data Address</TableCell>
                    <TableCell>Retry Index</TableCell>
                    <TableCell>Request ID</TableCell>
                    <TableCell>Label</TableCell>
                </TableHead>
                <TableBody>
                    {selectedNodeState.ndn.pit.map((eachPitEntry) => {
                        const key: number = hashCode(`${eachPitEntry.data_address},${eachPitEntry.request_id},${eachPitEntry.retry_index}`)
                        return <TableRow key={key}>
                            <TableCell>{eachPitEntry.data_address}</TableCell>
                            <TableCell>{eachPitEntry.retry_index}</TableCell>
                            <TableCell>{eachPitEntry.request_id}</TableCell>
                            <TableCell>{eachPitEntry.label}</TableCell>
                        </TableRow>
                    })}
                </TableBody>
            </Table>
        </TableContainer>
        <Typography variant="h6" gutterBottom align='center'>
            Package Counts for Incoming Packages
        </Typography>
        <TableContainer component={Paper}>
            <Table sx={{minWidth: "100%"}}>
                <TableHead>
                    <TableCell>Package Name</TableCell>
                    <TableCell>Package Count</TableCell>
                </TableHead>
                <TableBody>
                    <TableRow>
                        <TableCell>Hello</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.in.hello}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Hello Acknowledgement</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.in.hello_ack}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Interest</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.in.interest}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Data</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.in.data}</TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
        <Typography variant="h6" gutterBottom align='center'>
            Package Counts for Outgoing Packages
        </Typography>
        <TableContainer component={Paper}>
            <Table sx={{minWidth: "100%"}}>
                <TableHead>
                    <TableCell>Package Name</TableCell>
                    <TableCell>Package Count</TableCell>
                </TableHead>
                <TableBody>
                    <TableRow>
                        <TableCell>Hello</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.out.hello}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Hello Acknowledgement</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.out.hello_ack}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Interest Origin</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.out.interest_org}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Forwarded Interest</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.out.interest_fwd}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Data Origin</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.out.data_org}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Forwarded Data</TableCell>
                        <TableCell>{selectedNodeState.packet_counters.out.data_fwd}</TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
        <Typography variant="h6" gutterBottom align='center'>
            Last max 10 Packages
        </Typography>
        <TableContainer component={Paper}>
            <Table sx={{minWidth: "100%"}}>
                <TableHead>
                    <TableCell>Package</TableCell>
                </TableHead>
                <TableBody>
                    {selectedNodeState.last_10_packets.map((eachPackage) => {
                        return <TableRow key={hashCode(eachPackage)}>
                            <TableCell>{eachPackage}</TableCell>
                        </TableRow>
                    })}
                </TableBody>
            </Table>
        </TableContainer>
    </>;
    return element
}
