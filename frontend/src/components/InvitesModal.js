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

  // 🔹 Load invites when modal opens
  useEffect(() => {
    if (!show) return;
    setLoading(true);
    setError(null);

    axios
      .get(`${API_URL}/sessions/me/invites`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => {
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

  // 🔹 Accept invite (backend expects token, not ID)
  const acceptInvite = (invite) => {
    axios
      .post(
        `${API_URL}/sessions/invites/accept`,
        { token: invite.token },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      .then(() => {
        setInvites((prev) => prev.filter((inv) => inv.id !== invite.id));
        addFlashMessage("success", "Invitation accepted — opening session...");
        window.location.href = `/chat/${invite.session_id}`;
      })
      .catch((err) => {
        const msg = err.response?.data?.detail || err.message;
        addFlashMessage("danger", `Error accepting invite: ${msg}`);
      });
  };

  // 🔹 Decline invite (revoke endpoint)
  const declineInvite = (invite) => {
    axios
      .post(
        `${API_URL}/sessions/${invite.session_id}/invites/${invite.id}/revoke`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      )
      .then(() => {
        setInvites((prev) => prev.filter((inv) => inv.id !== invite.id));
        addFlashMessage("info", "Invitation declined");
      })
      .catch((err) => {
        const msg = err.response?.data?.detail || err.message;
        addFlashMessage("danger", `Error declining invite: ${msg}`);
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
                  onClick={() => acceptInvite(inv)}
                >
                  Accept
                </Button>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => declineInvite(inv)}
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
