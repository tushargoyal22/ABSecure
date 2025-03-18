import React from "react";
import { Routes, Route } from "react-router";
import Homepage from "./pages/Homepage";
import TrancheInput from "./pages/TrancheInput";
import TrancheResult from "./pages/TrancheResult";
import Dashboard from "./pages/Dashboard";
import Layout from "./components/Layout";
import Tranche from "./pages/Tranche";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Homepage />} />

      <Route
        path="/*"
        element={
          <Layout>
            <Routes>
              <Route path="tranche" element={<Tranche />} />
              <Route path="tranche-input" element={<TrancheInput />} />
              <Route path="tranche-result" element={<TrancheResult />} />
            </Routes>
          </Layout>
        }
      />
    </Routes>
  );
}

export default App;
