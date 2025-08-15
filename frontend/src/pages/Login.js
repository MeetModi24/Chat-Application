// src/pages/LoginPage.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useFlash } from "../contexts/FlashContext";
import "../styles/Login.css";

const API_URL = process.env.REACT_APP_API_URL;

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { addFlashMessage } = useFlash();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, remember_me: rememberMe }),
        credentials: "include",
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        login(data.access_token); // only pass token, AuthContext fetches user
        addFlashMessage("success", "Signed in successfully!");
        navigate("/");
      } else {
        addFlashMessage(
          "danger",
          data.detail || data.error || "Sign in failed."
        );
      }
    } catch (err) {
      addFlashMessage("danger", "Failed to connect to the server.");
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h2>Sign In</h2>
        <form onSubmit={handleSubmit}>
          <label className="form-label">Email</label>
          <input
            type="email"
            className="form-control"
            placeholder="someone@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <br />

          <label className="form-label">Password</label>
          <input
            type={showPassword ? "text" : "password"}
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <br />

          <div className="form-check">
            <input
              className="form-check-input"
              type="checkbox"
              checked={showPassword}
              onChange={() => setShowPassword(!showPassword)}
            />
            <label className="form-check-label text-success">
              Show Password
            </label>
          </div>
          <br />

          <div className="form-check mb-3">
            <input
              className="form-check-input"
              type="checkbox"
              checked={rememberMe}
              onChange={() => setRememberMe(!rememberMe)}
            />
            <label className="form-check-label">Remember Me</label>
          </div>

          <button type="submit" className="btn btn-primary w-100">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
