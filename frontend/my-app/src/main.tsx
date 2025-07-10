import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

// Clear all cookies (including sessionid, csrftoken) on app load
// Only for development/testing - remove for production!
document.cookie.split(';').forEach((c) => {
  document.cookie = c
    .replace(/^ +/, '')
    .replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/');
});
localStorage.clear();
sessionStorage.clear();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
