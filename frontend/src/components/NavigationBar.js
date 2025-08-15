// src/components/NavigationBar.js
import React from "react";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  FaHome,
  FaSignInAlt,
  FaUserPlus,
  FaComments,
  FaListAlt,
  FaSignOutAlt
} from "react-icons/fa";
import "../styles/Navbar.css";

const NavigationBar = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top" className="shadow-sm">
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-bold fs-4">
          ChatApp
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="nav" />
        <Navbar.Collapse id="nav">
          <Nav className="me-auto align-items-center">
            <Nav.Link as={Link} to="/" className="d-flex align-items-center">
              <FaHome className="me-1" /> Home
            </Nav.Link>

            {isAuthenticated && (
              <>
                <Nav.Link as={Link} to="/sessions" className="d-flex align-items-center">
                  <FaListAlt className="me-1" /> My Sessions
                </Nav.Link>
                <Nav.Link as={Link} to="/chat" className="d-flex align-items-center">
                  <FaComments className="me-1" /> Chat
                </Nav.Link>
              </>
            )}
          </Nav>

          <div className="d-flex align-items-center">
            {!isAuthenticated ? (
              <>
                <Button
                  as={Link}
                  to="/login"
                  variant="outline-light"
                  className="me-2 d-flex align-items-center"
                >
                  <FaSignInAlt className="me-1" /> Login
                </Button>
                <Button
                  as={Link}
                  to="/register"
                  variant="primary"
                  className="d-flex align-items-center"
                >
                  <FaUserPlus className="me-1" /> Sign Up
                </Button>
              </>
            ) : (
              <Button
                variant="danger"
                className="d-flex align-items-center"
                onClick={logout}
              >
                <FaSignOutAlt className="me-1" /> Logout
              </Button>
            )}
          </div>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default NavigationBar;
