import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Link, useNavigate } from "react-router";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import Swal from "sweetalert2";
import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL;

const Signup = () => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateEmail = (email) => /\S+@\S+\.\S+/.test(email);
  const validatePassword = (password) => password.length >= 6;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmedFullName = fullName.trim();

    if (!trimmedFullName) {
      return Swal.fire("Error", "Full Name is required!", "error");
    }
    if (!validateEmail(email)) {
      return Swal.fire("Error", "Invalid email format!", "error");
    }
    if (!validatePassword(password)) {
      return Swal.fire(
        "Error",
        "Password must be at least 6 characters!",
        "error"
      );
    }
    if (password !== confirmPassword) {
      return Swal.fire(
        "Error",
        "Password and Confirm Password do not match!",
        "error"
      );
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        full_name: trimmedFullName,
        email,
        password,
      });

      Swal.fire("Success", response.data.message, "success").then(() => {
        navigate("/login");
      });
    } catch (error) {
      Swal.fire(
        "Error",
        error.response?.data?.detail || "Registration failed",
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <Card className="w-full max-w-md shadow-lg bg-white dark:bg-gray-800">
        <CardHeader>
          <CardTitle className="text-center text-2xl font-semibold text-gray-800 dark:text-white">
            Create an Account
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="text"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="p-3 border border-white"
            />
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="p-3 border border-white"
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="p-3 border border-white"
            />
            <Input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="p-3 border border-white"
            />
            <Button
              type="submit"
              className="w-full py-3 font-semibold tracking-wide"
              disabled={loading}
            >
              {loading ? <Loader2 className="animate-spin" /> : "Sign Up"}
            </Button>
          </form>
          <div className="text-center text-gray-600 dark:text-gray-400 mt-4">
            <p>
              Already have an account?{" "}
              <Link
                to="/login"
                className="text-blue-600 dark:text-blue-400 font-medium"
              >
                Log in
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Signup;
