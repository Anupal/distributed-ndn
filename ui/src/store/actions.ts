import {NodeState} from "../types";
import {AsyncThunk, createAsyncThunk} from "@reduxjs/toolkit";
import {RootState} from "../index";
import axios from "axios";

export const fetchCurrentNodeState: AsyncThunk<
    { [label: string]: NodeState },
    void,
    { state: RootState }
> = createAsyncThunk<{ [label: string]: NodeState }, void, { state: RootState }>(
    "nodeState/fetchCurrentNodeState",
    async (arg, thunkAPI) => {
        const res = await axios.get('http://localhost:555/node-state', {
            responseType: "json",
        })

        return res.data
    }
)
