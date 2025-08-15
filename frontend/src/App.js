// src/App.js
import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import NavigationBar from "./components/NavigationBar";
import MainPage from "./pages/MainPage";
import Chat from "./pages/Chat";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Sessions from "./pages/Sessions";
import { AuthProvider } from "./contexts/AuthContext";
import { FlashProvider } from "./contexts/FlashContext";
import FlashMessages from "./components/FlashMessages";
import "./styles/base.css";

function App() {
  return (
    <AuthProvider>
      <FlashProvider>
        <Router>
          <NavigationBar />
          <FlashMessages /> {/* Global flash messages */}
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/chat/:id" element={<Chat />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/sessions" element={<Sessions />} />
          </Routes>
        </Router>
      </FlashProvider>
    </AuthProvider>
  );
}

export default App;
