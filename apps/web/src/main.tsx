import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";

// Supports both dev (`/`) and combined host (`/app/`) without code changes.
function basename(): string {
  if (typeof window !== "undefined" && window.location.pathname.startsWith("/app")) return "/app";
  return "/";
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root element");
ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <BrowserRouter basename={basename()}>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
