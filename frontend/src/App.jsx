import React from "react";
import { Routes, Route } from "react-router";
import TrancheInput from "./pages/TrancheInput";
import TrancheResult from "./pages/TrancheResult";
import Dashboard from "./pages/Dashboard";
import Layout from "./components/Layout";

function App() {
  return (
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tranche-input" element={<TrancheInput />} />
          <Route path="/tranche-result" element={<TrancheResult />} />
        </Routes>
      </Layout>
  );
}

export default App;
