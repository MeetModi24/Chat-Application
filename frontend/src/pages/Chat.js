import React, { useEffect, useState, useContext, useRef } from "react";
import { Form, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";
import { io } from "socket.io-client";
import "../styles/chat.css";

const Chat = () => {
  const { id } = useParams();
  const { token, user } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const socketRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    socketRef.current = io("http://localhost:8000", {
      auth: { token },
    });

    socketRef.current.emit("join_session", { session_id: id });

    socketRef.current.on("new_message", (msg) => {
      setMessages((prev) => [...prev, msg]);
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, [id, token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    if (input.trim() === "") return;
    const msg = {
      role: "user", // You can set role dynamically
      content: input,
      username: user.username,
    };
    socketRef.current.emit("send_message", { session_id: id, ...msg });
    setInput("");
  };

  const getBubbleClass = (role) => {
    switch (role) {
      case "user":
        return "message-bubble message-user";
      case "agent":
        return "message-bubble message-agent";
      case "system":
        return "message-system";
      default:
        return "message-bubble";
    }
  };

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.map((m, i) => (
          <div key={i} className={getBubbleClass(m.role)}>
            {m.role !== "system" && (
              <div className="message-username">{m.username}</div>
            )}
            {m.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <Form.Control
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <Button variant="success" onClick={sendMessage}>
          ➤
        </Button>
      </div>
    </div>
  );
};

export default Chat;
