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
        const res = await axios.get('https://macneill.scss.tcd.ie/~mathisn/scproj3/stats_2.json', {
            responseType: "json",
            withXSRFToken: true,
            withCredentials: true
        })

        return res.data
    }
)
