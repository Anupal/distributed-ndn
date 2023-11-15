import React, {useMemo, useState} from "react";
import {useAppSelector} from "../store/hooks";
import {EChart} from "@kbox-labs/react-echarts";
import {Grid, Paper} from "@mui/material";
import Typography from "@mui/material/Typography";
import {NodeState} from "../types";
import {NodeDetail} from "./NodeDetail";


const getNodeNameFromLabel = (label: number) => {
    return `${label}`
}

/**
 *     x, y -> visualized as position of nodes
 *     comm -> visualized using node tooltip
 *     packet_counters -> visualized in table of node details
 *     last_10_packets -> visualized in table of node details TODO
 *     data_address -> visualized using node tooltip
 *     label -> visualized using node label
 *     ndn
 *          fib -> visualized using edges between nodes and tooltips of edges
 *          pit -> visualized in table of node details TODO
 * **/
export const NodeGraph = () => {
    const nodesState = useAppSelector((state) => state.nodeStateReducer)

    const nodeStateKeys = useMemo(() => {
        return Object.keys(nodesState)
    }, [nodesState])

    const [selectedNodeLabel, setSelectedNodeLabel] = useState(null)

    const ips: string[] = useMemo(() => {
        return [...new Set(nodeStateKeys.map((eachKey) => {
            return nodesState[eachKey].comm.server_ip
        }))]
    }, [nodesState])

    const colors = ["blue", "green", "orange", "pink", "black", "magenta"]
    if (ips.length > colors.length) {
        throw new Error("Not enough IP colors!")
    }
    const ipColorMap: { [ip: string]: string } = useMemo(() => {
        const internalIpColorMap: { [ip: string]: string } = {}
        ips.forEach((eachIp, eachIndex) => {
            internalIpColorMap[eachIp] = colors[eachIndex]
        })
        return internalIpColorMap
    }, [ips]);


    const data = useMemo(() => {
        return nodeStateKeys.map((eachKey => {
            const eachNodeState = nodesState[eachKey]

            const ipColor = ipColorMap[eachNodeState.comm.server_ip]
            const nodeColor = eachNodeState.ndn.fib.length == 0 ? "red" : ipColor
            const opacity = eachNodeState.label == selectedNodeLabel ? 0.5 : 1
            const borderColor = eachNodeState.gw_node.is_node_marked ? "gold" : null
            return {
                name: getNodeNameFromLabel(eachNodeState.label),
                title: "hi",
                label: eachNodeState.label,
                gw_node_market: eachNodeState.gw_node,
                x: eachNodeState.x,
                y: eachNodeState.y,
                itemStyle: {
                    color: nodeColor,
                    borderWidth: 4,
                    opacity: opacity,
                    borderColor: borderColor
                },
            }
        }))
    }, [nodeStateKeys, selectedNodeLabel]);

    const links: { source: string, target: string }[] = useMemo(() => {
        return nodeStateKeys.flatMap((eachKey) => {
            const eachNodeState = nodesState[eachKey]
            const fromNodeName = getNodeNameFromLabel(eachNodeState.label)

            return eachNodeState.ndn.fib.map((eachFibEntry) => {
                return {
                    sourceLabel: eachNodeState.label,
                    targetLabel: eachFibEntry.label,
                    source: fromNodeName,
                    target: getNodeNameFromLabel(eachFibEntry.label)
                }
            })
        })
    }, [nodesState]);

    const onClickEvent = (sth: any) => {
        if (sth.dataType == "node") {
            setSelectedNodeLabel(sth.data.label)
        } else {
            console.log("node connection")
        }
    }

    return <Grid container spacing={2}>
        <Grid item xs={8}>
            <Paper style={{height: '100%', backgroundColor: '#ffffff'}}>
                <Typography variant="h5" gutterBottom align='center'>
                    P2P Network Graph
                </Typography>
                <EChart
                    className={"network-node-graph"}
                    style={{height: '89vh'}}
                    tooltip={{
                        formatter: (params: any) => {
                            if (params.dataType == "node") {
                                const singleNodeState: NodeState = nodesState[params.data.label]
                                let nodeMarketExtraContent = ""
                                if (singleNodeState.gw_node.is_node_marked) {
                                    nodeMarketExtraContent = `<br />External Node IP: ${singleNodeState.gw_node.peer_connection[0]} | External Node Port: ${singleNodeState.gw_node.peer_connection[1]}`
                                }
                                return `
               IP: ${singleNodeState.comm.server_ip} | Port: ${singleNodeState.comm.server_port}<br />
                Root Data Adress: ${singleNodeState.data_address}
                ` + nodeMarketExtraContent;
                            } else {
                                const sourceHelloCountForTarget = nodesState[params.data.sourceLabel].ndn.fib.filter((fibEntry) => fibEntry.label == params.data.targetLabel)[0].hello_count
                                const targetHelloCountForSource = nodesState[params.data.targetLabel].ndn.fib.filter((fibEntry) => fibEntry.label == params.data.sourceLabel)[0].hello_count
                                return `
                                ${params.data.source} Hello Count For ${params.data.target}: ${sourceHelloCountForTarget}<br />
                                ${params.data.target} Hello Count For ${params.data.source}: ${targetHelloCountForSource}
                                `
                            }
                        },
                    }}
                    series={[{
                        type: 'graph',
                        layout: 'none',
                        symbolSize: 50,
                        roam: true,
                        label: {
                            show: true
                        },
                        edgeSymbol: ['', 'arrow'],
                        edgeSymbolSize: [4, 10],
                        edgeLabel: {
                            fontSize: 20
                        },
                        data: data,
                        links: links,
                        lineStyle: {
                            opacity: 0.9,
                            width: 2,
                            curveness: 0
                        }
                    }]}
                    onClick={onClickEvent}
                />
            </Paper>
        </Grid>
        <Grid item xs={4}>
            <Paper style={{height: '100%', backgroundColor: '#ffffff'}}>
                <Typography variant="h5" gutterBottom align='center'>
                    Node Details for Node {selectedNodeLabel}
                </Typography>
                {selectedNodeLabel == null ? null :
                    <NodeDetail selectedNodeState={nodesState[selectedNodeLabel]}/>
                }
            </Paper>
        </Grid>
    </Grid>
}
