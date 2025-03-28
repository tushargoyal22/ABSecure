import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useTranche } from "@/context/TrancheContext";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as ReTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { useNavigate } from "react-router";
import { HelpCircle } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import Swal from "sweetalert2";

const TrancheAllocationResult = () => {
  const navigate = useNavigate();
  const { criteria, suboption, budget, trancheDetails, setSelectedTranche } =
    useTranche();
  const [isTrancheInfoOpen, setIsTrancheInfoOpen] = useState(false);
  const [selectedTranche, setSelectedTranchee] = useState(null);

  if (
    !criteria ||
    !suboption ||
    !budget ||
    !trancheDetails ||
    trancheDetails.length === 0
  ) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center">
        <p className="text-lg text-gray-600 dark:text-gray-300">
          No allocation data available. Please allocate tranches first.
        </p>
        <Button className="mt-6" onClick={() => navigate("/tranche-input")}>
          Enter Criterion
        </Button>
      </div>
    );
  }

  const chartData = trancheDetails.map((t) => ({
    name: t.tranche_name,
    budgetSpent: t.budget_spent,
  }));

  const pieData = trancheDetails.map((t) => ({
    name: t.tranche_name,
    value: t.loans_allocated,
  }));

  const COLORS = ["#4CAF50", "#FF9800", "#F44336", "#9C27B0"];
  const trancheColorMap = trancheDetails.reduce((acc, tranche, index) => {
    acc[tranche.tranche_name] = COLORS[index % COLORS.length];
    return acc;
  }, {});

  const handleCheckout = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      Swal.fire({
        toast: true,
        position: "bottom-end",
        icon: "error",
        title: "Unauthorized",
        text: "You must be logged in to buy a tranche.",
        showConfirmButton: false,
        timer: 5000,
        timerProgressBar: true,
      });
      setTimeout(() => {
        navigate("/login");
      }, 3000);

      setLoading(false);
      return;
    }

    const selectedTrancheInfo = trancheDetails.find(
      (t) => t.tranche_name === selectedTranche
    );

    if (selectedTrancheInfo) {
      setSelectedTranche(JSON.stringify(selectedTrancheInfo));

      Swal.fire({
        title: "Confirm Checkout",
        text: `You have selected ${selectedTrancheInfo.tranche_name}. Proceed to checkout?`,
        icon: "info",
        showCancelButton: true,
        confirmButtonText: "Yes, proceed",
        cancelButtonText: "Cancel",
      }).then((result) => {
        if (result.isConfirmed) {
          navigate("/checkout");
        }
      });
    }
  };

  return (
    <div className="flex flex-col items-center p-6 space-y-8 min-h-screen ">
      <Card className="w-full max-w-4xl shadow-xl rounded-2xl bg-white dark:bg-gray-800 p-6">
        <CardHeader className="border-b pb-4 flex justify-between items-center">
          <CardTitle className="text-4xl font-bold text-gray-800 dark:text-gray-200">
            Tranche Allocation Summary
          </CardTitle>
        </CardHeader>

        <CardContent>
          <div className="mb-6 mt-5 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
              Investor Input:
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Criteria:{" "}
              <span className="font-medium text-gray-800 dark:text-gray-200">
                {criteria}
              </span>
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              Sub-option:{" "}
              <span className="font-medium text-gray-800 dark:text-gray-200">
                {suboption}
              </span>
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              Budget:{" "}
              <span className="font-medium text-gray-800 dark:text-gray-200">
                ${budget}
              </span>
            </p>
          </div>

          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mt-10">
            Allocated Tranches:
          </h3>
          <table className="w-full text-left border-collapse mt-4 bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
            <thead>
              <tr className="bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                <th className="p-3">
                  Tranche{" "}
                  <Dialog
                    open={isTrancheInfoOpen}
                    onOpenChange={setIsTrancheInfoOpen}
                  >
                    <DialogTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <HelpCircle
                          size={24}
                          className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                        />
                      </Button>
                    </DialogTrigger>
                    <DialogTitle></DialogTitle>
                    <DialogContent>
                      <DialogHeader>
                        <h3 className="text-xl font-semibold">
                          What are Tranches?
                        </h3>
                      </DialogHeader>
                      <DialogDescription className="text-gray-600 dark:text-gray-300">
                        Tranches are different portions of an investment with
                        varying risk, return, and priority. Senior tranches are
                        paid first but have lower returns, while junior tranches
                        offer higher returns with more risk.
                      </DialogDescription>
                      <Button onClick={() => navigate("/tranche")}>
                        Learn More
                      </Button>
                    </DialogContent>
                  </Dialog>
                </th>
                <th className="p-3">
                  <Tooltip>
                    <TooltipTrigger>Risk</TooltipTrigger>
                    <TooltipContent>
                      Higher risk can mean higher returns.
                    </TooltipContent>
                  </Tooltip>
                </th>
                <th className="p-3">
                  <Tooltip>
                    <TooltipTrigger>Return</TooltipTrigger>
                    <TooltipContent>
                      Potential return based on tranche type.
                    </TooltipContent>
                  </Tooltip>
                </th>
                <th className="p-3">Loans Allocated</th>
                <th className="p-3">Amount</th>
                <th className="p-3">
                  <Tooltip>
                    <TooltipTrigger>Priority</TooltipTrigger>
                    <TooltipContent>
                      Senior tranches are paid first.
                    </TooltipContent>
                  </Tooltip>
                </th>
                <th className="p-3">Select</th>
              </tr>
            </thead>
            <tbody>
              {trancheDetails.map((tranche, index) => (
                <tr
                  key={index}
                  className={`border-b transition-colors cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 ${
                    selectedTranche === tranche.tranche_name
                      ? "bg-gray-200 dark:bg-gray-700"
                      : ""
                  }`}
                  onClick={() => setSelectedTranchee(tranche.tranche_name)}
                >
                  <td className="p-3 font-medium text-gray-800 dark:text-gray-200">
                    {tranche.tranche_name}
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {tranche.risk_category}
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {tranche.return_category}
                  </td>
                  <td className="p-3 font-medium text-blue-600 dark:text-blue-400">
                    {tranche.loans_allocated}
                  </td>
                  <td className="p-3 font-medium text-green-600 dark:text-green-400">
                    ${tranche.budget_spent}
                  </td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">
                    {tranche.payment_priority}
                  </td>
                  <td className="p-5">
                    <Checkbox
                      checked={selectedTranche === tranche.tranche_name}
                      onCheckedChange={() =>
                        setSelectedTranchee(tranche.tranche_name)
                      }
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Budget Allocation Across Tranches:
              </h3>
              <ResponsiveContainer width="100%" height={300} className="mt-4">
                <BarChart
                  data={chartData}
                  className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700"
                >
                  <XAxis dataKey="name" tick={{ fill: "#4A5568" }} />
                  <YAxis tick={{ fill: "#4A5568" }} />
                  <ReTooltip
                    contentStyle={{ backgroundColor: "#fff", color: "#000" }}
                    wrapperStyle={{ borderRadius: "8px" }}
                  />
                  <Legend wrapperStyle={{ color: "#4A5568" }} />
                  <Bar
                    dataKey="budgetSpent"
                    barSize={40}
                    radius={[10, 10, 0, 0]}
                  >
                    {chartData.map((entry) => (
                      <Cell
                        key={entry.name}
                        fill={trancheColorMap[entry.name]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Loan Distribution Across Tranche
              </h3>
              <ResponsiveContainer width="100%" height={300} className="mt-4">
                <PieChart className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 shadow-lg">
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {pieData.map((entry, index) => (
                      <Cell
                        key={entry.name}
                        fill={trancheColorMap[entry.name]}
                      />
                    ))}
                  </Pie>
                  <ReTooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-8 flex justify-between">
            <Button onClick={() => navigate("/tranche-input")}>
              Modify Allocation
            </Button>
            <Button onClick={() => navigate("/report")}>
              Generate Securitization Report
            </Button>
            <Button
              disabled={!selectedTranche}
              onClick={handleCheckout}
              className="px-6 py-2 font-medium rounded-lg"
            >
              Checkout
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrancheAllocationResult;
