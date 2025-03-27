import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Clock } from "lucide-react";
import { useNavigate } from "react-router";
import { useUser } from "@/context/UserContext";
const API_URL = import.meta.env.VITE_API_URL;
import Swal from "sweetalert2";

const CRITERIA = {
  Duration: ["Short-Term", "Medium-Term", "Long-Term"],
  Creditworthiness: ["Excellent", "Good", "Fair", "Poor"],
  "ML-Based Risk": ["Low-Risk", "Medium-Risk", "High-Risk"],
  Liquidity: ["High Liquidity", "Medium Liquidity", "Low Liquidity"],
  "Debt Analysis": ["Low Debt", "Moderate Debt", "High Debt"],
  "Financial Liabilities": [
    "Not Trustable",
    "Moderate Trustable",
    "Highly Trustable",
  ],
  Age: ["Young Borrowers", "Mid-Career Borrowers", "Senior Borrowers"],
  "Financial Status": ["High Income", "Medium Income", "Low Income"],
};

const TrancheMarketplace = () => {
  const [tranches, setTranches] = useState([]);
  const [filteredTranches, setFilteredTranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [criteria, setCriteria] = useState("");
  const [suboption, setSuboption] = useState("");
  const [amountAllocated, setAmountAllocated] = useState("");
  const navigate = useNavigate();
  const { user } = useUser();

  useEffect(() => {
    const fetchTranches = async () => {
      try {
        const response = await axios.get(`${API_URL}/tranch/available`);
        setTranches(response.data);
        setFilteredTranches(response.data);
      } catch (error) {
        console.error("Error fetching available tranches:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTranches();
  }, []);

  const handleInvest = async (tranche) => {
    if (!user) return;
    try {
      const investorId = user.id;

      const response = await axios.post(
        `${API_URL}/tranch/buy-tranche?tranche_id=${tranche._id}&investor_id=${investorId}`
      );

      if (response.status === 200) {
        Swal.fire({
          title: "Transaction Successful!",
          text: "Your investment has been processed.",
          icon: "success",
          confirmButtonText: "OK",
        }).then(() => navigate("/portfolio"));

        setTranches(tranches.filter((t) => t._id !== tranche._id));
        setFilteredTranches(
          filteredTranches.filter((t) => t._id !== tranche._id)
        );
      }
    } catch (error) {
      console.error("Error buying tranche:", error);
      Swal.fire({
        title: "Transaction Failed!",
        text:
          error.response?.data?.detail ||
          "An error occurred. Please try again.",
        icon: "error",
        confirmButtonText: "Retry",
      });
    }
  };

  const handleFilter = () => {
    let filtered = tranches.filter(
      (tranche) =>
        (!criteria || tranche.criteria === criteria) &&
        (!suboption || tranche.suboption === suboption) &&
        (!amountAllocated ||
          tranche.budget_spent <= parseFloat(amountAllocated))
    );
    setFilteredTranches(filtered);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-4xl font-bold text-center mb-8 text-gray-900 dark:text-gray-100">
        Available Tranches
      </h1>

      <div className="flex flex-wrap gap-4 mb-6 justify-center">
        <select
          value={criteria}
          onChange={(e) => setCriteria(e.target.value)}
          className="border p-2 rounded-md dark:bg-gray-800 dark:text-white"
        >
          <option value="">Select Criteria</option>
          {Object.keys(CRITERIA).map((key) => (
            <option key={key} value={key}>
              {key}
            </option>
          ))}
        </select>
        <select
          value={suboption}
          onChange={(e) => setSuboption(e.target.value)}
          className="border p-2 rounded-md dark:bg-gray-800 dark:text-white"
          disabled={!criteria}
        >
          <option value="">Select Suboption</option>
          {criteria &&
            CRITERIA[criteria].map((sub) => (
              <option key={sub} value={sub}>
                {sub}
              </option>
            ))}
        </select>
        <input
          type="number"
          placeholder="Max Amount Allocated"
          value={amountAllocated}
          onChange={(e) => setAmountAllocated(e.target.value)}
          className="border p-2 rounded-md dark:bg-gray-800 dark:text-white"
        />
        <Button
          onClick={handleFilter}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg"
        >
          Apply Filters
        </Button>
      </div>

      {filteredTranches.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">
          No matching tranches found.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredTranches.map((tranche) => (
            <Card
              key={tranche._id}
              className="shadow-lg border rounded-xl p-6 bg-white dark:bg-gray-800 dark:border-gray-700"
            >
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {tranche.tranche_name}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-md text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Amount:</span> $
                  {tranche.budget_spent}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Criteria:</span>{" "}
                  {tranche.criteria}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Suboption:</span>{" "}
                  {tranche.suboption}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Risk Level:</span>{" "}
                  {tranche.risk_category}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Average Risk:</span>{" "}
                  {parseFloat(tranche.average_risk).toFixed(3)}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Return Rate:</span>{" "}
                  {tranche.return_category}
                </p>
                <p className="text-sm text-red-500 flex items-center gap-2 mt-2">
                  <Clock className="w-4 h-4" /> Expires soon
                </p>
                <Button
                  className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg dark:bg-blue-500 dark:hover:bg-blue-600"
                  onClick={() => handleInvest(tranche)}
                  disabled={!user}
                >
                  {user ? "Invest Now" : "Sign in to Invest"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default TrancheMarketplace;
