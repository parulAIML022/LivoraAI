import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "@/components/ProtectedRoute";
import Home from "./pages/Home";
import SignIn from "./pages/SignIn";
import SignUp from "./pages/SignUp";
import Register from "./pages/Register";
import DonorDashboard from "./pages/DonorDashboard";
import RecipientDashboard from "./pages/RecipientDashboard";
import HospitalDashboard from "./pages/HospitalDashboard";
import CoordinatorDashboard from "./pages/CoordinatorDashboard";
import NotFound from "./pages/NotFound";
import Otp from "./pages/otp";
import UserProfile from "./pages/UserProfile";
import About from "./pages/About";
import HowItWorks from "./pages/HowItWorks";
import FAQ from "./pages/FAQ";
import Contact from "./pages/Contact";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/login" element={<Navigate to="/signin" replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/otp" element={<Otp />} />

        <Route path="/about" element={<About />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/howitworks" element={<Navigate to="/how-it-works" replace />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/contact" element={<Contact />} />

        <Route
          path="/donor-dashboard"
          element={
            <ProtectedRoute allowedRoles={["donor"]}>
              <DonorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recipient-dashboard"
          element={
            <ProtectedRoute allowedRoles={["recipient"]}>
              <RecipientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/hospital-dashboard"
          element={
            <ProtectedRoute allowedRoles={["hospital"]}>
              <HospitalDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/coordinator-dashboard"
          element={
            <ProtectedRoute allowedRoles={["admin", "coordinator"]}>
              <CoordinatorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute
              allowedRoles={["donor", "recipient", "hospital", "admin", "coordinator"]}
            >
              <UserProfile />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
