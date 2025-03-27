import React, { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranche } from "@/context/TrancheContext";
import { useNavigate } from "react-router";
import Swal from "sweetalert2";
import { Loader2, CheckCircle, XCircle } from "lucide-react";
import { useUser } from "@/context/UserContext";
import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL;

const Execution = () => {
  const navigate = useNavigate();
  const { selectedTranche, trancheDetails, criteria, suboption } = useTranche();
  const { user } = useUser();
  const [transactionStatus, setTransactionStatus] = useState("pending");
  const hasExecuted = useRef(false);

  useEffect(() => {
    if (!user) {
      Swal.fire({
        title: "User must be signed in",
        icon: "error",
      });
      navigate("/login");
    }

    if (!selectedTranche || !trancheDetails.length) {
      navigate("/tranche-result");
      return;
    }

    if (hasExecuted.current) return;
    hasExecuted.current = true;

    const executeCheckout = async () => {
      try {
        const parsedTranche = JSON.parse(selectedTranche);
        const updatedTrancheDetails = trancheDetails.map((tranche) => ({
          ...tranche,
          investor_id:
            tranche.tranche_name === parsedTranche.tranche_name
              ? user.id
              : tranche.investor_id,
          criteria,
          suboption,
        }));

        const response = await axios.post(
          `${API_URL}/tranch/checkout`,
          updatedTrancheDetails
        );
        
        if (response.status === 200) {
          setTransactionStatus("success");
          Swal.fire({
            title: "Transaction Successful!",
            text: "Your investment has been processed.",
            icon: "success",
            confirmButtonText: "OK",
          }).then(() => navigate("/portfolio"));
        }
      } catch (error) {
        setTransactionStatus("failed");
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
    executeCheckout();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <Card className="w-full max-w-lg shadow-xl rounded-2xl bg-white dark:bg-gray-800 p-6 text-center">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            Transaction Execution
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-6">
          {transactionStatus === "pending" && (
            <>
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
              <p className="text-gray-700 dark:text-gray-300">
                Processing your investment...
              </p>
            </>
          )}

          {transactionStatus === "success" && (
            <>
              <CheckCircle className="w-12 h-12 text-green-500" />
              <p className="text-green-600 font-semibold">
                Transaction Successful!
              </p>
            </>
          )}

          {transactionStatus === "failed" && (
            <>
              <XCircle className="w-12 h-12 text-red-500" />
              <p className="text-red-600 font-semibold">
                Transaction Failed! Please try again.
              </p>
              <Button
                onClick={() => navigate("/tranche-result")}
                variant="outline"
              >
                Retry
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Execution;
