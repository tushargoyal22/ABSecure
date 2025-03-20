import React, { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranche } from "../context/TrancheContext";
import Swal from "sweetalert2";
import axios from "axios";
import { useNavigate } from "react-router";
const API_URL = import.meta.env.VITE_API_URL;

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

const TrancheInput = () => {
  const navigate = useNavigate();
  const { setCriteria, setSuboption, setBudget, setTrancheDetails, setReport } =
    useTranche();
  const [selectedCriterion, setSelectedCriterion] = useState("");
  const [selectedSubCriterion, setSelectedSubCriterion] = useState("");
  const [budget, setBudgetLocal] = useState("");
  const [errors, setErrors] = useState({});

  const validateInputs = () => {
    let newErrors = {};
    if (!selectedCriterion) newErrors.criterion = "Please select a criterion.";
    if (!selectedSubCriterion)
      newErrors.subCriterion = "Please select a sub-criterion.";
    if (!budget) newErrors.budget = "Please enter a budget amount.";
    else if (isNaN(budget) || budget <= 0)
      newErrors.budget = "Enter a valid positive budget amount.";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateInputs()) return;

    setCriteria(selectedCriterion);
    setSuboption(selectedSubCriterion);
    setBudget(budget);

    Swal.fire({
      title: "Calculating Tranches...",
      text: "Please wait while we process your request.",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    try {
      const response = await axios.post(
        `${API_URL}/pool/allocate?criterion=${selectedCriterion}&suboption=${selectedSubCriterion}&investor_budget=${budget}`
      );

      setTrancheDetails(response.data.tranche_details);
      setReport(null);

      Swal.fire({
        icon: "success",
        title: "Tranches Allocated",
        text: "Tranche allocation completed successfully!",
        confirmButtonText: "View Results",
      }).then((result) => {
        if (result.isConfirmed) {
          navigate("/tranche-result");
        }
      });
    } catch (error) {
      console.error("Error allocating tranches:", error);

      Swal.fire({
        icon: "error",
        title: "Allocation Failed",
        text: "There was an issue allocating tranches. Please try again.",
      });
    }
  };

  return (
    <div className="flex flex-col justify-center items-center w-full h-full p-6 overflow-hidden">
      <Card className="w-full max-w-lg mx-auto mt-10 p-6 shadow-lg dark:bg-black">
        <CardHeader>
          <CardTitle>Tranche Allocation</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <Select onValueChange={setSelectedCriterion}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a Criterion" />
                </SelectTrigger>
                <SelectContent>
                  {Object.keys(CRITERIA).map((criterion) => (
                    <SelectItem key={criterion} value={criterion}>
                      {criterion}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.criterion && (
                <p className="text-red-500 text-sm">{errors.criterion}</p>
              )}
            </div>

            <div>
              <Select
                onValueChange={setSelectedSubCriterion}
                disabled={!selectedCriterion}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select a Sub-Criterion" />
                </SelectTrigger>
                <SelectContent>
                  {selectedCriterion &&
                    CRITERIA[selectedCriterion].map((subCriterion) => (
                      <SelectItem key={subCriterion} value={subCriterion}>
                        {subCriterion}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              {errors.subCriterion && (
                <p className="text-red-500 text-sm">{errors.subCriterion}</p>
              )}
            </div>

            <div>
              <Input
                type="number"
                placeholder="Enter Budget ($)"
                value={budget}
                onChange={(e) => setBudgetLocal(e.target.value)}
                min="1"
              />
              {errors.budget && (
                <p className="text-red-500 text-sm">{errors.budget}</p>
              )}
            </div>

            <Button type="submit" className="w-full">
              Allocate
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrancheInput;
