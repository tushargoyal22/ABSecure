import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Link, useNavigate } from "react-router";
import axios from "axios";
import Swal from "sweetalert2";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useUser } from "@/context/UserContext";
const API_URL = import.meta.env.VITE_API_URL;

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginUser } = useUser();

  const validateEmail = (email) => /\S+@\S+\.\S+/.test(email);
  const validatePassword = (password) => password.length >= 6;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateEmail(formData.email)) {
      return Swal.fire("Error", "Invalid email format!", "error");
    }
    if (!validatePassword(formData.password)) {
      return Swal.fire(
        "Error",
        "Password must be at least 6 characters!",
        "error"
      );
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/auth/login`,
        new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            Accept: "application/json",
          },
        }
      );
      const userData = response.data;

      loginUser(userData);
      localStorage.setItem("token", response.data.access_token);

      Swal.fire("Success", "Login successful!", "success").then(() => {
        navigate("/dashboard");
      });
    } catch (error) {
      Swal.fire(
        "Error",
        error.response?.data?.error || "Login failed",
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
            Welcome Back
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              placeholder="Email"
              value={formData.email}
              name="email"
              onChange={handleChange}
              required
              className="p-3 border border-white"
            />
            <Input
              type="password"
              placeholder="Password"
              value={formData.password}
              name="password"
              onChange={handleChange}
              required
              className="p-3 border border-white"
            />
            <Button
              type="submit"
              className="w-full py-3 font-semibold tracking-wide"
              disabled={loading}
            >
              {loading ? <Loader2 className="animate-spin" /> : "Sign In"}
            </Button>
          </form>
          <div className="text-center text-gray-600 dark:text-gray-400 mt-4">
            <p>
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="text-blue-600 dark:text-blue-400 font-medium"
              >
                Sign up
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
