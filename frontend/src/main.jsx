import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { BrowserRouter } from "react-router";
import { TrancheProvider } from "./context/TrancheContext";
import { UserProvider } from "./context/UserContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <UserProvider>
        <TrancheProvider>
          <App />
        </TrancheProvider>
      </UserProvider>
    </BrowserRouter>
  </StrictMode>
);
