// src/contexts/FlashContext.js
import React, { createContext, useContext, useState, useCallback } from "react";

const FlashContext = createContext();

export function FlashProvider({ children }) {
  const [flashMessages, setFlashMessages] = useState([]);

  const addFlashMessage = useCallback((type, message) => {
    setFlashMessages((prev) => [...prev, [type, message]]);
  }, []);

  const removeFlashMessage = useCallback((index) => {
    setFlashMessages((prev) => prev.filter((_, i) => i !== index));
  }, []);

  return (
    <FlashContext.Provider
      value={{ flashMessages, addFlashMessage, removeFlashMessage }}
    >
      {children}
    </FlashContext.Provider>
  );
}

export function useFlash() {
  return useContext(FlashContext);
}
