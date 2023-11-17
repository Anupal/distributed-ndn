import express from 'express';
import dotenv from 'dotenv';
import axios from "axios";
import * as https from "https";

dotenv.config();

const app = express();
const port = 5555;

app.get('/node-state', async (req, res) => {
    const instance = axios.create({
        httpsAgent: new https.Agent({
            rejectUnauthorized: false
        })
    });

    const promisePi2 = (instance.get('https://macneill.scss.tcd.ie/~anmishra/scproj3/stats_1.json', {
        responseType: "json",
    }))
    const resultPi2 = (await promisePi2).data
    //There were some issues doing both requests in parallel
    const promisePi1 = (instance.get('https://macneill.scss.tcd.ie/~mathisn/scproj3/stats_2.json', {
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

