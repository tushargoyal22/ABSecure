import axios from "axios";
import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import Swal from "sweetalert2";
const API_URL = import.meta.env.VITE_API_URL;

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const token = searchParams.get("token"); 

  useEffect(() => {
    if (!token) {
      Swal.fire({
        icon: "error",
        title: "Invalid Link",
        text: "No verification token found!",
      }).then(() => navigate("/login"));
      return;
    }

    const verifyEmail = async () => {
      try {
        const response = await axios.get(`${API_URL}/auth/verify-email?${searchParams}`);


        if (response.status==200) {
          Swal.fire({
            icon: "success",
            title: "Email Verified!",
            text: "Your account has been successfully verified. You can now log in.",
          }).then(() => navigate("/login"));
        } else {
          Swal.fire({
            icon: "error",
            title: "Verification Failed",
            text: data.message || "Invalid or expired verification link.",
          }).then(() => navigate("/login"));
        }
      } catch (error) {
        Swal.fire({
          icon: "error",
          title: "Server Error",
          text: "Something went wrong. Please try again later.",
        }).then(() => navigate("/login"));
      } finally {
        setLoading(false);
      }
    };

    verifyEmail();
  }, [token, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        {loading ? (
          <p className="text-lg font-semibold">Verifying your email...</p>
        ) : (
          <p className="text-lg font-semibold">Redirecting...</p>
        )}
      </div>
    </div>
  );
};

export default VerifyEmail;
