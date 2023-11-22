import * as React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import {Grid, Paper} from "@mui/material";
import {NodeGraph} from "./components/NodeGraph";

export default function App() {
    return (
        <Container>
            <Typography variant="h2" gutterBottom >
                Scalable Computing Project Two - UI
            </Typography>
            <NodeGraph/>
        </Container>
    );
}
