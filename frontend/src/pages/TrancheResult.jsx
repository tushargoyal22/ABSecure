import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useTranche } from "../context/TrancheContext";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { useNavigate } from "react-router";

const TrancheAllocationResult = () => {
  const navigate = useNavigate();
  const { criteria, suboption, budget, trancheDetails } = useTranche();

  if (
    !criteria ||
    !suboption ||
    !budget ||
    !trancheDetails ||
    trancheDetails.length === 0
  ) {
    return (
      <div className="text-center text-gray-500 text-lg font-medium flex flex-col items-center">
        No allocation data available. Please allocate tranches first.
        <div className="mt-8 flex justify-center">
          <Button
            className=" px-4 py-2"
            onClick={() => navigate("/tranche-input")}
          >
            Enter Criterion
          </Button>
        </div>
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

  return (
    <div className="flex flex-col items-center p-8 space-y-8 min-h-screen">
      <Card className="w-full max-w-4xl shadow-xl rounded-xl bg-white dark:bg-gray-800 p-6">
        <CardHeader className="border-b pb-4">
          <CardTitle className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            Tranche Allocation Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg shadow-sm">
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

          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mt-6">
            Allocated Tranches:
          </h3>
          <table className="w-full text-left border-collapse mt-4 bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
            <thead>
              <tr className="bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                <th className="p-3">Tranche</th>
                <th className="p-3">Risk</th>
                <th className="p-3">Return</th>
                <th className="p-3">Loans Allocated</th>
                <th className="p-3">Amount</th>
                <th className="p-3">Priority</th>
              </tr>
            </thead>
            <tbody>
              {trancheDetails.map((tranche, index) => (
                <tr
                  key={index}
                  className="border-b hover:bg-gray-100 dark:hover:bg-gray-600"
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
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Risk vs. Return Analysis:
              </h3>
              <ResponsiveContainer width="100%" height={300} className="mt-4">
                <BarChart
                  data={chartData}
                  className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow"
                >
                  <XAxis dataKey="name" tick={{ fill: "#4A5568" }} />
                  <YAxis tick={{ fill: "#4A5568" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#fff", color: "#000" }}
                    wrapperStyle={{ borderRadius: "8px" }}
                  />
                  <Legend wrapperStyle={{ color: "#4A5568" }} />
                  <Bar
                    dataKey="budgetSpent"
                    fill="#4CAF50"
                    barSize={40}
                    radius={[10, 10, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                Loans Allocation:
              </h3>
              <ResponsiveContainer width="100%" height={300} className="mt-4">
                <PieChart>
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
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-8 flex ">
            <Button onClick={() => navigate("/tranche-input")}>
              Modify Allocation
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrancheAllocationResult;
