import React, { useEffect, useState, useContext } from "react";
import { Container, Button, ListGroup, Row, Col, Form, Card } from "react-bootstrap";
import axios from "axios";
import { AuthContext } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const Sessions = () => {
  const { token } = useContext(AuthContext);
  const [sessions, setSessions] = useState([]);
  const [newSessionName, setNewSessionName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      // TODO: Replace with your backend endpoint
      const res = await axios.get("/sessions", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSessions(res.data);
    } catch (err) {
      console.error("Error fetching sessions");
    }
  };

  const createSession = async () => {
    try {
      // TODO: Replace with your backend endpoint
      await axios.post(
        "/sessions",
        { name: newSessionName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewSessionName("");
      fetchSessions();
    } catch (err) {
      console.error("Error creating session");
    }
  };

  const deleteSession = async (id) => {
    try {
      // TODO: Replace with your backend endpoint
      await axios.delete(`/sessions/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchSessions();
    } catch (err) {
      console.error("Error deleting session");
    }
  };

  return (
    <Container className="mt-4">
      <Row>
        <Col md={6}>
          <Card>
            <Card.Body>
              <h4>My Chat Sessions</h4>
              <ListGroup>
                {sessions.map((s) => (
                  <ListGroup.Item
                    key={s.id}
                    className="d-flex justify-content-between align-items-center"
                  >
                    <span>{s.name}</span>
                    <div>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => navigate(`/chat/${s.id}`)}
                        className="me-2"
                      >
                        Open
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => deleteSession(s.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Body>
              <h4>Create New Session</h4>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Session Name</Form.Label>
                  <Form.Control
                    type="text"
                    value={newSessionName}
                    onChange={(e) => setNewSessionName(e.target.value)}
                  />
                </Form.Group>
                <Button variant="success" onClick={createSession}>
                  Create
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Sessions;
