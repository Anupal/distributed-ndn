import {NodeState} from "../types";
import {AsyncThunk, createAsyncThunk} from "@reduxjs/toolkit";
import {RootState} from "../index";

export const fetchCurrentNodeState: AsyncThunk<
    { [label: string]: NodeState },
    void,
    { state: RootState }
> = createAsyncThunk<{ [label: string]: NodeState }, void, { state: RootState }>(
    "nodeState/fetchCurrentNodeState",
    async (arg, thunkAPI) => {
        return await (await fetch('sample_node_state.json', {
            method: "GET",
            mode: "no-cors",
            redirect: 'follow'
        })).json() as { [label: string]: NodeState }
    }
)
