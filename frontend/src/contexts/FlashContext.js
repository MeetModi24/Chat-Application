// src/context/FlashContext.js
import React, { createContext, useContext, useState, useCallback } from "react";

const FlashContext = createContext();

export function FlashProvider({ children }) {
  const [flashMessages, setFlashMessages] = useState([]);

  const addFlashMessage = useCallback((type, message) => {
    setFlashMessages((prev) => [...prev, [type, message]]);
  }, []);

  return React.createElement(
    FlashContext.Provider,
    { value: { flashMessages, addFlashMessage } },
    children
  );
}

export function useFlash() {
  return useContext(FlashContext);
}
