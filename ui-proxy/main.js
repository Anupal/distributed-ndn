import express from 'express';
import dotenv from 'dotenv';
import axios from "axios";


//Bypass for error when fetching current node state (Certificate validation)
//From: https://github.com/axios/axios/issues/4847
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

dotenv.config();

const app = express();
const port = process.env.PORT;

app.get('/node-state', async (req, res) => {
    const promisePi1 = (axios.get('https://macneill.scss.tcd.ie/~mathisn/scproj3/stats_2.json', {
        responseType: "json",
    }))
    const promisePi2 = (axios.get('https://macneill.scss.tcd.ie/~anmishra/scproj3/stats_1.json', {
        responseType: "json",
    }))
    const resultPi1 = (await promisePi1).data
    const resultPi2 = (await promisePi2).data
    res.send({...resultPi1, ...resultPi2});
});

app.use(express.static("../ui/build"))

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});

