// src/index.js
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import {AuthProvider} from "./contexts/AuthContext";
import "bootstrap/dist/css/bootstrap.min.css";
import "./index.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import { FlashProvider } from "./contexts/FlashContext";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <AuthProvider>
    <FlashProvider>
    <App />
    </FlashProvider>
  </AuthProvider>
);
