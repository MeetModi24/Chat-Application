// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const API_URL = process.env.REACT_APP_API_URL;

  // Load user info if token exists
  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      fetchUserData(token);
    } else {
      localStorage.removeItem("token");
      setUser(null);
    }
  }, [token]);

  const fetchUserData = async (jwtToken) => {
    try {
      const res = await fetch(`${API_URL}/users/me`, {
        method: "GET",
        headers: { Authorization: `Bearer ${jwtToken}` },
      });
      if (!res.ok) throw new Error("Failed to fetch user");
      const data = await res.json();
      setUser(data);
    } catch (error) {
      console.error("Error fetching user:", error);
      logout();
    }
  };

  const login = (jwtToken) => {
    setToken(jwtToken); // triggers fetchUserData in useEffect
  };

  const logout = () => {
    setToken("");
    setUser(null);
    localStorage.removeItem("token");
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider
      value={{ user, token, login, logout, isAuthenticated }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
