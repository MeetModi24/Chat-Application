import React, { useEffect, useState, useContext } from "react";
import {
  Container,
  Button,
  Row,
  Col,
  Form,
  Card,
  Spinner,
} from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import { AuthContext } from "../contexts/AuthContext";
import { useFlash } from "../contexts/FlashContext";
import { Plus, Trash, ChatDots } from "react-bootstrap-icons";
import "../styles/Sessions.css";


const Sessions = () => {
  const { token } = useContext(AuthContext);
  const { addFlashMessage } = useFlash();
  const navigate = useNavigate();

  const [sessions, setSessions] = useState([]);
  const [newSessionName, setNewSessionName] = useState("");
  const [loading, setLoading] = useState(true);
  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    fetchSessions();
    // eslint-disable-next-line
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/sessions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSessions(res.data);
    } catch (err) {
      addFlashMessage("danger", "Failed to load sessions.");
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    if (!newSessionName.trim()) {
      addFlashMessage("warning", "Please enter a session title.");
      return;
    }
    try {
      await axios.post(
        `${API_URL}/sessions`,
        { title: newSessionName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewSessionName("");
      addFlashMessage("success", "Session created!");
      fetchSessions();
    } catch (err) {
      addFlashMessage("danger", "Error creating session.");
    }
  };

  const deleteSession = async (id) => {
    if (!window.confirm("Are you sure you want to delete this session?")) return;
    try {
      await axios.delete(`${API_URL}/sessions/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      addFlashMessage("success", "Session deleted.");
      fetchSessions();
    } catch (err) {
      addFlashMessage("danger", "Error deleting session.");
    }
  };

  return (
    <Container className="mt-4">
      <Row>
        {/* Create session form */}
        <Col md={4}>
          <Card className="shadow-sm">
            <Card.Body>
              <h5 className="mb-3">Create New Session</h5>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Control
                    type="text"
                    placeholder="Enter session title..."
                    value={newSessionName}
                    onChange={(e) => setNewSessionName(e.target.value)}
                  />
                </Form.Group>
                <Button variant="success" onClick={createSession} className="w-100">
                  <Plus className="me-1" /> Create
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        {/* Sessions list */}
        <Col md={8}>
          <h5 className="mb-3">My Chat Sessions</h5>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
            </div>
          ) : sessions.length === 0 ? (
            <p className="text-muted">No sessions yet. Create one to start chatting!</p>
          ) : (
            <Row xs={1} sm={2} lg={3} className="g-3">
              {sessions.map((s) => (
                <Col key={s.id}>
                  <Card
                    className="h-100 shadow-sm session-card"
                    style={{ cursor: "pointer" }}
                    onClick={() => navigate(`/chat/${s.id}`)}
                  >
                    <Card.Body className="d-flex flex-column justify-content-between">
                      <div>
                        <ChatDots className="text-primary me-2" size={20} />
                        <strong>{s.title}</strong>
                        <p className="text-muted small mb-0">
                          Created: {dayjs(s.created_at).isValid()
                            ? dayjs(s.created_at).format("MMM D, YYYY h:mm A")
                            : "Unknown date"}
                        </p>
                      </div>
                      <div className="text-end mt-3">
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteSession(s.id);
                          }}
                        >
                          <Trash size={16} />
                        </Button>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Sessions;
