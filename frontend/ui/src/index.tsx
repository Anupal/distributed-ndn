import * as React from 'react';
import * as ReactDOM from 'react-dom/client';
import CssBaseline from '@mui/material/CssBaseline';
import {ThemeProvider} from '@mui/material/styles';
import App from './App';
import theme from './theme';
import {configureStore} from "@reduxjs/toolkit";
import {Provider} from "react-redux";
import {NodeStateReducer} from "./store/reducers";
import {fetchCurrentNodeState} from "./store/actions";
import axios from "axios";

const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement!);

const store = configureStore({
    reducer: {
        nodeStateReducer: NodeStateReducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(),
})
// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch

root.render(
    <ThemeProvider theme={theme}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
        <CssBaseline/>
        <Provider store={store}>
            <App/>
        </Provider>
    </ThemeProvider>,
);
