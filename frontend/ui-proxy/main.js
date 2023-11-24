import express from 'express';
import dotenv from 'dotenv';
import axios from "axios";
import * as https from "https";
import {Constants} from "../constants.js";
import * as constants from "constants";

dotenv.config();

const app = express();
const port = Constants.application_port;

app.get('/node-state', async (req, res) => {
    const instance = axios.create({
        httpsAgent: new https.Agent({
            rejectUnauthorized: false
        })
    });

    const promisePi2 = (instance.get(`${constants.node_state1_url}/stats_1.json`, {
        responseType: "json",
    }))
    const resultPi2 = (await promisePi2).data
    //There were some issues doing both requests in parallel
    const promisePi1 = (instance.get(`${constants.node_state2_url}/stats_1.json`, {
        responseType: "json",
    }))
    const resultPi1 = (await promisePi1).data

    console.log("WAS PASSIERT HIER?")

    res.send({...resultPi1, ...resultPi2});
});

app.use(express.static("../ui/build"))

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});

