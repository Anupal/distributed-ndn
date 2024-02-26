import {createSlice} from "@reduxjs/toolkit";
import {NodeState} from "../types";
import {fetchCurrentNodeState} from "./actions";

const initialNodeState: { [label: string]: NodeState } = {}
const InitialNodeStateSlice = createSlice({
    name: "initialNodeState",
    initialState: initialNodeState as { [label: string]: NodeState },
    reducers: {},
    extraReducers: builder => builder.addCase(fetchCurrentNodeState.fulfilled, (_, action) => {
        return action.payload
    })
})

export const NodeStateReducer = InitialNodeStateSlice.reducer
