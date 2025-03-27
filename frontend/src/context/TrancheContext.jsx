import React, { createContext, useState, useEffect, useContext } from "react";

export const TrancheContext = createContext();

export const TrancheProvider = ({ children }) => {
  const [criteria, setCriteria] = useState(
    () => localStorage.getItem("criteria") || ""
  );
  const [suboption, setSuboption] = useState(
    () => localStorage.getItem("suboption") || ""
  );
  const [budget, setBudget] = useState(
    () => parseFloat(localStorage.getItem("budget")) || null
  );
  const [trancheDetails, setTrancheDetails] = useState(() => {
    const storedData = localStorage.getItem("trancheDetails");
    return storedData ? JSON.parse(storedData) : null;
  });
  const [report, setReport] = useState(() => {
    const storedReport = localStorage.getItem("report");
    return storedReport ? JSON.parse(storedReport) : null;
  });
  const [selectedTranche, setSelectedTranche] = useState(() => {
    const storedData = localStorage.getItem("selectedTranche");
    return storedData ? JSON.parse(storedData) : null;
  });
  

  useEffect(() => {
    localStorage.setItem("criteria", criteria);
    localStorage.setItem("suboption", suboption);
    localStorage.setItem("budget", budget);
    localStorage.setItem("trancheDetails", JSON.stringify(trancheDetails));
    localStorage.setItem("report", JSON.stringify(report));
    localStorage.setItem("selectedTranche", JSON.stringify(selectedTranche));
  }, [criteria, suboption, budget, trancheDetails, report, selectedTranche]);

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
        selectedTranche,
        setSelectedTranche,
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
