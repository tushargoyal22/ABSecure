import React from "react";
import { Routes, Route } from "react-router";
import Homepage from "./pages/Homepage";
import TrancheInput from "./pages/TrancheInput";
import TrancheResult from "./pages/TrancheResult";
import Dashboard from "./pages/Dashboard";
import Layout from "./components/Layout";
import Tranche from "./pages/Tranche";
import ReportViewer from "./pages/ReportViewer";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import { ThemeProvider } from "./components/ui/theme-provider";
import VerifyEmail from "./pages/VerifyMail";
import Execution from "./pages/BuyingExecution";
import TrancheMarketplace from "./pages/TrancheMarketplace";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/verify" element={<VerifyEmail />} />

        <Route
          path="/*"
          element={
            <Layout>
              <Routes>
                <Route path="tranche" element={<Tranche />} />
                <Route path="tranche-input" element={<TrancheInput />} />
                <Route path="tranche-result" element={<TrancheResult />} />
                <Route path="checkout" element={<Execution />} />
                <Route path="report" element={<ReportViewer />} />
                <Route path="marketplace" element={<TrancheMarketplace />} />
                <Route path="dashboard" element={<Dashboard />} />
              </Routes>
            </Layout>
          }
        />
      </Routes>
    </ThemeProvider>
  );
}

export default App;
