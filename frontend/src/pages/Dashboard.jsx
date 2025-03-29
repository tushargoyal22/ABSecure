import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Legend,
  CartesianGrid,
} from "recharts";
import { useUser } from "@/context/UserContext";
import Swal from "sweetalert2";
import { useNavigate } from "react-router";
import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL;
const colors = ["#22c55e", "#facc15", "#ef4444", "#3b82f6"];

const Dashboard = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [tranches, setTranches] = useState([]);
  const [trancheDetails, setTrancheDetails] = useState([]);
  const [budget, setBudget] = useState(0);
  const [spent, setSpent] = useState(0);
  const [riskScore, setRiskScore] = useState(0);
  const [riskDistribution, setRiskDistribution] = useState({});
  const [diversityScore, setDiversityScore] = useState(0);
  const [returnDistribution, setReturnDistribution] = useState({});
  const [loanCount, setLoanCount] = useState(0);
  const [loanDistribution, setLoanDistribution] = useState([]);
  const [paymentPriority, setPaymentPriority] = useState({});

  useEffect(() => {
    if (!user) {
      Swal.fire({
        title: "User must be signed in",
        icon: "error",
      });
      navigate("/login");
      return;
    }

    const fetchUserTranches = async () => {
      try {
        const response = await axios.get(`${API_URL}/tranch/user-tranches`, {
          params: { user_id: user.id },
        });

        if (response.status === 200) {
          setTranches(response.data.tranches || []);
        }
      } catch (error) {
        console.error("Error fetching user tranches:", error);
      }
    };
    fetchUserTranches();
  }, [user]);

  useEffect(() => {
    if (tranches.length === 0) return;

    const fetchTrancheDetails = async () => {
      try {
        const details = await Promise.all(
          tranches.map(async (trancheId) => {
            const response = await axios.get(`${API_URL}/tranch/tranche`, {
              params: { tranche_id: trancheId },
            });
            return response.data;
          })
        );
        setTrancheDetails(details);

        const totalInvestorBudget = details.reduce(
          (sum, tranche) => sum + (tranche.investor_budget || 0),
          0
        );
        setBudget(totalInvestorBudget);

        const totalInvestorSpent = details.reduce(
          (sum, tranche) => sum + (tranche.budget_spent || 0),
          0
        );
        setSpent(totalInvestorSpent);

        const avgRisk =
          details.reduce(
            (sum, t) => sum + (t.average_risk * t.budget_spent || 0),
            0
          ) / totalInvestorSpent || 0;
        setRiskScore(avgRisk.toFixed(2));
        setDiversityScore(new Set(details.map((t) => t.name)).size);

        const riskDist = details.reduce((acc, tranche) => {
          acc[tranche.risk_category] =
            (acc[tranche.risk_category] || 0) + tranche.budget_spent;
          return acc;
        }, {});
        setRiskDistribution(riskDist);

        const retDist = details.reduce((acc, t) => {
          acc[t.return_category] =
            (acc[t.return_category] || 0) + t.budget_spent;
          return acc;
        }, {});
        setReturnDistribution(retDist);

        const totalLoans = details.reduce(
          (sum, t) => sum + (t.loans?.length || 0),
          0
        );
        setLoanCount(totalLoans);

        const loanDist = details.map((t) => ({
          name: t.tranche_name,
          loans: t.loans?.length || 0,
        }));
        setLoanDistribution(loanDist);

        const priorityDist = details.reduce((acc, t) => {
          acc[t.payment_priority] =
            (acc[t.payment_priority] || 0) + t.budget_spent;
          return acc;
        }, {});
        setPaymentPriority(priorityDist);
      } catch (error) {
        console.error("Error fetching tranche details:", error);
      }
    };

    fetchTrancheDetails();
  }, [tranches]);

  return (
    <div className="min-h-screen p-6 dark:bg-gray-900 dark:text-white bg-gray-100 text-black">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Investor Dashboard</h1>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="bg-blue-600 text-white">
          <CardHeader>
            <CardTitle>Total Investment</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl">${spent}</p>
          </CardContent>
        </Card>
        <Card className="bg-yellow-500 text-white">
          <CardHeader>
            <CardTitle>Available Budget</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl">${budget - spent}</p>
          </CardContent>
        </Card>
        <Card className="bg-red-500 text-white">
          <CardHeader>
            <CardTitle>Portfolio Risk Score</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl">{riskScore}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(riskDistribution).map(
                    ([key, value], index) => ({
                      name: key,
                      value,
                      color: colors[index % colors.length],
                    })
                  )}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={110}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {Object.entries(riskDistribution).map((_, index) => (
                    <Cell key={index} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Investment by Return Category</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(returnDistribution).map(
                    ([key, value], index) => ({
                      name: key,
                      value,
                      color: colors[index % colors.length],
                    })
                  )}
                  cx="50%"
                  cy="50%"
                  outerRadius={110}
                  dataKey="value"
                  label
                >
                  {Object.entries(returnDistribution).map((_, index) => (
                    <Cell key={index} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className=" p-6 dark:bg-gray-900 dark:text-white bg-gray-100 text-black">
        <h2 className="text-xl font-semibold mt-6">
          Number of Loans Across Tranches
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={loanDistribution}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#ddd" />
            <XAxis stroke="#888" tick={{ fontSize: 12 }} />
            <YAxis stroke="#888" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: "#222", color: "#fff" }}
            />
            <Legend
              verticalAlign="top"
              wrapperStyle={{ fontSize: 14, color: "#fff" }}
            />
            <Bar
              dataKey="loans"
              fill="#3b82f6"
              barSize={40}
              radius={[5, 5, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <h2 className="text-xl font-semibold mt-6">Investment History</h2>
      <table className="w-full mt-3 border-collapse border border-gray-300 dark:border-gray-600">
        <thead>
          <tr className="bg-gray-200 dark:bg-gray-800">
            <th className="border border-gray-300 p-2">Tranche</th>
            <th className="border border-gray-300 p-2">Risk Category</th>
            <th className="border border-gray-300 p-2">Return Category</th>
            <th className="border border-gray-300 p-2">Investment</th>
            <th className="border border-gray-300 p-2">Payment Priority</th>
          </tr>
        </thead>
        <tbody>
          {trancheDetails.map((t, index) => (
            <tr key={index} className="border border-gray-300">
              <td className="border border-gray-300 p-2">{t.tranche_name}</td>
              <td className="border border-gray-300 p-2">{t.risk_category}</td>
              <td className="border border-gray-300 p-2">
                {t.return_category}
              </td>
              <td className="border border-gray-300 p-2">${t.budget_spent}</td>
              <td className="border border-gray-300 p-2">
                {t.payment_priority}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
