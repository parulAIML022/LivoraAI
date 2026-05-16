import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Heart } from "lucide-react";
const medicalHero = "/placeholder.svg";

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="animate-fade-in">
              <div className="flex items-center space-x-3 mb-8">
                <div className="bg-gradient-to-r from-cyan-400 to-blue-500 p-3 rounded-xl">
                  <Heart className="h-8 w-8 text-white" />
                </div>
                <span className="text-3xl font-bold text-gray-800">LIVORA</span>
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 animate-slide-up">
                A Life-Saving
                <span className="block text-transparent bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text">
                  Connection
                </span>
              </h1>

              <p
                className="text-xl text-gray-600 mb-8 max-w-xl animate-fade-in"
                style={{ animationDelay: "0.2s" }}
              >
                Connecting donors, recipients, and hospitals in real-time with AI
              </p>

              <div
                className="flex flex-col sm:flex-row gap-4 animate-scale-in"
                style={{ animationDelay: "0.4s" }}
              >
                <Link to="/signup">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                  >
                    Register as Donor
                  </Button>
                </Link>

                <Link to="/signup">
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-2 border-blue-500 text-blue-600 hover:bg-blue-50 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300"
                  >
                    Find a Donor
                  </Button>
                </Link>
              </div>
            </div>

            {/* Right Content - Medical Illustration */}
            <div
              className="relative animate-scale-in"
              style={{ animationDelay: "0.6s" }}
            >
              <div className="relative">
                <img
                  src={medicalHero}
                  alt="Medical illustration showing organ donation process"
                  className="w-full h-auto rounded-2xl shadow-2xl"
                />
                <div className="absolute -top-4 -right-4 bg-gradient-to-r from-cyan-400 to-blue-500 p-4 rounded-full animate-pulse">
                  <Heart className="h-8 w-8 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="bg-blue-600 text-white mt-16 py-12">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-8">
          {/* Logo and About */}
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="bg-white p-2 rounded-lg">
                <Heart className="text-blue-600 h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Livora</h3>
            </div>
            <p className="text-sm leading-relaxed">
              Advanced AI technology matching organ donors with recipients,
              bringing hope to families and saving lives every day.
            </p>
            <div className="mt-4 text-sm space-y-1">
              <p>📧 support@livora.ai</p>
              <p>📞 1-800-LIVORA-1</p>
              <p>📍 24/7 Emergency Support</p>
            </div>
          </div>

          {/* Platform Links */}
          <div>
            <h4 className="font-semibold mb-3">Platform</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/howitworks" className="hover:underline">How It Works</Link></li>
              <li><Link to="/about" className="hover:underline">About Us</Link></li>
              <li><Link to="/faq" className="hover:underline">FAQ</Link></li>
              <li><Link to="/contact" className="hover:underline">Contact</Link></li>
            </ul>
          </div>

          {/* Services Links */}
          <div>
            <h4 className="font-semibold mb-3">Services</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/signup" className="hover:underline">For Donors</Link></li>
              <li><Link to="/signup" className="hover:underline">For Recipients</Link></li>
              <li><Link to="/signup" className="hover:underline">For Hospitals</Link></li>
              <li><Link to="/support" className="hover:underline">Emergency Support</Link></li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="font-semibold mb-3">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/privacy" className="hover:underline">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:underline">Terms of Service</Link></li>
              <li><Link to="/guidelines" className="hover:underline">Medical Guidelines</Link></li>
              <li><Link to="/compliance" className="hover:underline">Compliance</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-blue-400 mt-10 pt-6 text-center text-sm">
          © 2024 Livora. All rights reserved. Saving lives through technology.
        </div>
      </footer>
    </div>
  );
};

export default Home;
