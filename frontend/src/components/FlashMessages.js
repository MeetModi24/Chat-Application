// src/components/FlashMessages.js
import React, { useEffect } from "react";
import { useFlash } from "../contexts/FlashContext";

export default function FlashMessages() {
  const { flashMessages, removeFlashMessage } = useFlash();

  // Auto-dismiss after 3 seconds
  useEffect(() => {
    if (flashMessages.length > 0) {
      const timers = flashMessages.map((_, idx) =>
        setTimeout(() => removeFlashMessage(idx), 3000)
      );
      return () => timers.forEach((t) => clearTimeout(t));
    }
  }, [flashMessages, removeFlashMessage]);

  if (flashMessages.length === 0) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 10,
        right: 10,
        zIndex: 2000,
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
            onClick={() => removeFlashMessage(idx)}
          ></button>
        </div>
      ))}
    </div>
  );
}
