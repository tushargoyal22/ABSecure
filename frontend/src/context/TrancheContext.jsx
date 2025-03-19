import React, { createContext, useState, useEffect, useContext } from "react";

export const TrancheContext = createContext();

export const TrancheProvider = ({ children }) => {
  const [criteria, setCriteria] = useState(() => localStorage.getItem("criteria") || "");
  const [suboption, setSuboption] = useState(() => localStorage.getItem("suboption") || "");
  const [budget, setBudget] = useState(() => parseFloat(localStorage.getItem("budget")) || null);
  const [trancheDetails, setTrancheDetails] = useState(() => {
    const storedData = localStorage.getItem("trancheDetails");
    return storedData ? JSON.parse(storedData) : null;
  });
  const [report, setReport] = useState(() => {
    const storedReport = localStorage.getItem("report");
    return storedReport ? JSON.parse(storedReport) : null;
  });

  useEffect(() => {
    localStorage.setItem("criteria", criteria);
    localStorage.setItem("suboption", suboption);
    localStorage.setItem("budget", budget);
    localStorage.setItem("trancheDetails", JSON.stringify(trancheDetails));
    localStorage.setItem("report", JSON.stringify(report));
  }, [criteria, suboption, budget, trancheDetails, report]);

  return (
    <TrancheContext.Provider
      value={{
        criteria,
        setCriteria,
        suboption,
        setSuboption,
        budget,
        setBudget,
        trancheDetails,
        setTrancheDetails,
        report,
        setReport, 
      }}
    >
      {children}
    </TrancheContext.Provider>
  );
};

export const useTranche = () => {
  const context = useContext(TrancheContext);
  return context;
};
