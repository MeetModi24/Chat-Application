import React, { useState, useEffect } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Spinner from "react-bootstrap/Spinner";
import Alert from "react-bootstrap/Alert";
import axios from "axios";
import { useFlash } from "../contexts/FlashContext";
import { useAuth } from "../contexts/AuthContext";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function InvitesModal({ show, onClose }) {
  const { addFlashMessage } = useFlash();
  const { token } = useAuth();

  const [loading, setLoading] = useState(false);
  const [invites, setInvites] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!show) return;
    setLoading(true);
    setError(null);

    axios
      .get(`${API_URL}/sessions/invites`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
        // Ensure invites is always an array
        setInvites(Array.isArray(res.data) ? res.data : []);
      })
      .catch((err) => {
        const errData = err.response?.data;
        const msg =
          typeof errData?.detail === "string"
            ? errData.detail
            : errData?.detail?.msg || err.message;
        setError(msg);
        addFlashMessage("danger", `Error loading invitations: ${msg}`);
      })
      .finally(() => setLoading(false));
  }, [show, token, addFlashMessage]);

  const respondToInvite = (inviteId, status) => {
    axios
      .post(
        `${API_URL}/sessions/invites/${inviteId}/respond`,
        { status },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      .then(() => {
        setInvites((prev) => prev.filter((inv) => inv.id !== inviteId));
        addFlashMessage(
          "success",
          status === "accepted"
            ? "Invitation accepted — opening session..."
            : "Invitation declined"
        );

        if (status === "accepted") {
          const invite = invites.find((i) => i.id === inviteId);
          if (invite) {
            window.location.href = `/chat/${invite.session_id}`;
          }
        }
      })
      .catch((err) => {
        const errData = err.response?.data;
        const msg =
          typeof errData?.detail === "string"
            ? errData.detail
            : errData?.detail?.msg || err.message;
        addFlashMessage("danger", `Error updating invitation: ${msg}`);
      });
  };

  const renderError = () => {
    if (!error) return null;
    return (
      <Alert variant="danger">
        {typeof error === "string" ? error : JSON.stringify(error)}
      </Alert>
    );
  };

  return (
    <Modal show={show} onHide={onClose} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>Pending Chat Invitations</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading && (
          <div className="text-center py-4">
            <Spinner animation="border" />
          </div>
        )}

        {renderError()}

        {!loading && !error && invites.length === 0 && (
          <Alert variant="info">No pending invitations.</Alert>
        )}

        {!loading &&
          !error &&
          invites.map((inv) => (
            <div
              key={inv.id}
              className="d-flex justify-content-between align-items-center border p-2 mb-2"
            >
              <div>
                <strong>{inv.session_name}</strong>
                <div className="text-muted small">
                  Invited by {inv.inviter_email}
                </div>
              </div>
              <div>
                <Button
                  variant="success"
                  size="sm"
                  className="me-2"
                  onClick={() => respondToInvite(inv.id, "accepted")}
                >
                  Accept
                </Button>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => respondToInvite(inv.id, "declined")}
                >
                  Decline
                </Button>
              </div>
            </div>
          ))}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
