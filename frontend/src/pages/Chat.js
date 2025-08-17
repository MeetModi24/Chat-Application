import React, { useEffect, useRef, useState, useContext, useMemo } from "react";
import { useParams } from "react-router-dom";
import { Form, Button, Spinner, Badge } from "react-bootstrap";
import axios from "axios";
import dayjs from "dayjs";
import { AuthContext } from "../contexts/AuthContext";
import { useFlash } from "../contexts/FlashContext";
import "../styles/chat.css";

/**
 * Build a ws:// or wss:// URL from an HTTP API base.
 * e.g. http://localhost:8000 -> ws://localhost:8000
 */
function buildWsUrl(httpBase) {
  if (!httpBase) return "";
  try {
    const u = new URL(httpBase);
    u.protocol = u.protocol === "https:" ? "wss:" : "ws:";
    return u.origin;
  } catch {
    return httpBase.replace(/^http/, "ws");
  }
}

export default function Chat() {
  const { id: sessionId } = useParams();
  const { token, user } = useContext(AuthContext);
  const { addFlashMessage } = useFlash();

  const API_URL = process.env.REACT_APP_API_URL;
  const WS_ORIGIN = useMemo(() => buildWsUrl(API_URL), [API_URL]);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [connecting, setConnecting] = useState(true);
  const [wsReady, setWsReady] = useState(false);

  const wsRef = useRef(null);
  const endRef = useRef(null);

  // Load message history (REST)
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoadingHistory(true);
      try {
        const res = await axios.get(`${API_URL}/sessions/${sessionId}/messages`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { limit: 200, order_desc: false },
        });
        if (!cancelled) setMessages(res.data || []);
      } catch (e) {
        if (!cancelled) addFlashMessage("danger", "Failed to load chat history.");
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    };
    if (sessionId && token) load();
    return () => {
      cancelled = true;
    };
  }, [API_URL, sessionId, token, addFlashMessage]);

  // Connect WebSocket
  useEffect(() => {
    if (!sessionId || !token) return;

    setConnecting(true);
    setWsReady(false);

    // ws://localhost:8000/ws/sessions/<id>?token=<JWT>
    const wsUrl = `${WS_ORIGIN}/ws/sessions/${sessionId}?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnecting(false);
      setWsReady(true);
    };

    ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        const enriched = {
          id: `live-${Date.now()}-${Math.random().toString(36).slice(2)}`,
          role: data.role || "system",
          content: data.content || "",
          user_id: data.user_id || null,
          username: data.username || null,
          created_at: data.created_at || new Date().toISOString(),
        };
        setMessages((prev) => [...prev, enriched]);
      } catch {
        // ignore malformed
      }
    };

    ws.onclose = () => {
      setWsReady(false);
    };

    ws.onerror = () => {
      setWsReady(false);
      addFlashMessage("danger", "WebSocket error.");
    };

    return () => {
      try {
        ws.close();
      } catch {}
    };
  }, [WS_ORIGIN, sessionId, token, addFlashMessage]);

  // Auto-scroll to bottom
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    const text = input.trim();
    if (!text || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    const payload = {
      role: "user",
      content: text,
      // tool_calls, metadata optional
    };

    try {
      wsRef.current.send(JSON.stringify(payload));
      setInput("");
      // No optimistic append; server broadcasts back (including to sender)
    } catch {
      addFlashMessage("danger", "Failed to send message.");
    }
  };

  const bubbleClass = (role) => {
    if (role === "user") return "bubble bubble-user";
    if (role === "agent") return "bubble bubble-agent";
    if (role === "system") return "bubble bubble-system";
    return "bubble";
  };

  const prettyTime = (iso) =>
    iso && dayjs(iso).isValid() ? dayjs(iso).format("HH:mm") : "";

  return (
    <div className="chat-page">
      <div className="chat-wrapper">
        {/* Header */}
        <header className="chat-header">
          <div className="chat-title">
            <div className="chat-avatar">
              {user?.username?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="chat-title-text">
              <h5 className="m-0">Session</h5>
              <small className="text-muted">#{sessionId?.slice(0, 8)}</small>
            </div>
          </div>

          <div className="chat-status">
            {loadingHistory && (
              <span className="me-2">
                <Spinner animation="border" size="sm" /> Loading…
              </span>
            )}
            <Badge bg={wsReady ? "success" : connecting ? "warning" : "danger"}>
              {wsReady ? "Connected" : connecting ? "Connecting…" : "Disconnected"}
            </Badge>
          </div>
        </header>

        {/* Body */}
        <main className="chat-body">
          {loadingHistory ? (
            <div className="chat-loading">
              <Spinner animation="border" />
            </div>
          ) : (
            <>
              {messages.map((m) => (
                <div key={m.id || `${m.created_at}-${Math.random()}`}>
                  {m.role === "system" ? (
                    <div className={bubbleClass(m.role)}>
                      <small className="text-muted">{m.content}</small>
                    </div>
                  ) : (
                    <div className={`message-row ${m.role === "user" ? "right" : "left"}`}>
                      {m.role !== "user" && <div className="avatar">A</div>}
                      <div className={bubbleClass(m.role)}>
                        <div className="bubble-meta">
                          <span className="name">
                            {m.user_id === user?.id
                              ? "You"
                              : m.username || "Participant"}
                          </span>

                          <span className="time">{prettyTime(m.created_at)}</span>
                        </div>
                        <div className="bubble-text">{m.content}</div>
                      </div>
                      {m.role === "user" && (
                        <div className="avatar user">
                          {m.user_id === user?.id
                            ? (user?.username?.[0]?.toUpperCase() || "U")
                            : (m.username?.[0]?.toUpperCase() || "P")}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              <div ref={endRef} />
            </>
          )}
        </main>

        {/* Input */}
        <footer className="chat-input">
          <Form.Control
            type="text"
            placeholder={wsReady ? "Type a message…" : "Connecting…"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={!wsReady}
            className="chat-input-field"
          />
          <Button
            variant="primary"
            className="send-btn"
            onClick={sendMessage}
            disabled={!wsReady || !input.trim()}
          >
            Send
          </Button>
        </footer>
      </div>
    </div>
  );
}
