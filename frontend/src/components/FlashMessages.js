// src/components/FlashMessages.js
import React, { useEffect } from "react";
import { useFlash } from "../contexts/FlashContext";

export default function FlashMessages() {
  const { flashMessages, removeFlashMessage } = useFlash();

  // Auto-remove after 5 seconds
  useEffect(() => {
    if (flashMessages.length > 0) {
      const timers = flashMessages.map((_, index) =>
        setTimeout(() => {
          removeFlashMessage(index);
        }, 5000)
      );
      return () => timers.forEach((t) => clearTimeout(t));
    }
  }, [flashMessages, removeFlashMessage]);

  if (flashMessages.length === 0) return null;

  return (
    <div
      className="flash-container"
      style={{
        position: "fixed",
        top: 10,
        right: 10,
        zIndex: 1000,
        maxWidth: "300px",
      }}
    >
      {flashMessages.map(([type, message], idx) => (
        <div
          key={idx}
          className={`alert alert-${type} alert-dismissible fade show mb-2`}
          role="alert"
        >
          {message}
          <button
            type="button"
            className="btn-close"
            aria-label="Close"
            onClick={() => removeFlashMessage(idx)}
          ></button>
        </div>
      ))}
    </div>
  );
}
