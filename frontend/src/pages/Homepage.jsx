import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, Sun, Moon, Star } from "lucide-react";
import { Link } from "react-router";
import { pricingPlans, testimonials } from "../constants/config";

const Homepage = () => {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-black'} flex flex-col items-center p-8 transition-all duration-300`}>
      <div className="absolute top-4 right-4 flex gap-4">
        <Button onClick={() => setDarkMode(!darkMode)} className="border px-4 py-2 rounded-xl">
          {darkMode ? <Sun /> : <Moon />}
        </Button>
        <Link to="/login">
          <Button variant="outline" className="border-white text-black dark:text-white px-4 py-2 rounded-xl">
            Login
          </Button>
        </Link>
        <Link to="/signup">
          <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-4 py-2 rounded-xl">
            Sign Up
          </Button>
        </Link>
      </div>

      <div className="max-w-4xl mt-40 text-center space-y-8">
        <h1 className="text-5xl font-extrabold leading-tight">
          Welcome to <span className="text-yellow-300">ABSecure</span>
        </h1>
        <p className="text-lg">
          Empowering investors with insights and risk assessment for Asset-Backed Securities.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/tranche-input">
            <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-6 py-3 rounded-2xl">
              Explore Tranches <ArrowRight className="ml-2" />
            </Button>
          </Link>
          <Link to="/tranche">
            <Button variant="outline" className="border-white text-black dark:text-white px-6 py-3 rounded-2xl">
              Learn Financial Terms
            </Button>
          </Link>
        </div>

        <section className="py-16 mt-16 w-full rounded-2xl shadow-lg">
          <h2 className="text-3xl font-bold text-center">Pricing Plans</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10 px-8">
            {pricingPlans.map((plan, idx) => (
              <Card key={idx} className="p-4 hover:scale-105 transition-transform duration-300">
                <CardContent>
                  <h3 className="text-xl font-bold">{plan.name} Plan</h3>
                  <p className="text-sm mt-2">{plan.description}</p>
                  <p className="font-bold mt-4">{plan.price}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="text-center py-16 mt-16">
          <h2 className="text-3xl font-bold">Testimonials</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 px-8 mt-8">
            {testimonials.map((testimonial, idx) => (
              <Card key={idx} className="p-4">
                <CardContent>
                  <p className="italic">"{testimonial.quote}"</p>
                  <p className="font-bold mt-4">- {testimonial.name}</p>
                  <div className="flex justify-center mt-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="text-yellow-400" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="text-center py-16 mt-16">
          <h2 className="text-3xl font-bold">Get Started Today!</h2>
          <p className="text-lg mt-4">
            Join ABSecure and take control of your investments with smart tools and insights.
          </p>
          <Link to="/signup">
            <Button className="mt-6 bg-yellow-400 hover:bg-yellow-500 text-black px-6 py-3 rounded-2xl">
              Sign Up Now
            </Button>
          </Link>
        </section>
      </div>
    </div>
  );
};

export default Homepage;
