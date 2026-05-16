import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";
import { saveRoleProfileAfterSignup } from "@/lib/saveRoleProfile";

const Register = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    phone: "",
    location: "",
    bloodGroup: "",
    organ: "",
    history: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    if (formData.password.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }

    setIsSubmitting(true);
    try {
      await signup({
        fullName: formData.fullName,
        email: formData.email,
        password: formData.password,
        role: "donor",
      });
      await saveRoleProfileAfterSignup("donor", {
        phone: formData.phone,
        location: formData.location,
        bloodGroup: formData.bloodGroup,
        organType: formData.organ,
        medicalHistory: formData.history,
        hospitalName: "",
      });
      toast.success("Donor account created");
      navigate("/donor-dashboard");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Registration failed.";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center bg-gray-50">
      <div className="max-w-4xl w-full bg-white shadow-lg rounded-lg p-10">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-2xl font-bold text-green-600">Organ Donor</h2>
            <p className="text-gray-500">Fill out the form below to register</p>
          </div>
          <button
            onClick={() => navigate("/register")}
            className="text-blue-600 border px-4 py-2 rounded-lg hover:bg-gray-100"
          >
            Change Role
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-600 mb-2">Full Name *</label>
            <input
              type="text"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              placeholder="Enter your full name"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Email Address *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Password *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Confirm Password *</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Phone Number *</label>
            <input
              type="text"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="Enter your phone number"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Location *</label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="City, State, Country"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Blood Group *</label>
            <select
              name="bloodGroup"
              value={formData.bloodGroup}
              onChange={handleChange}
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
              required
            >
              <option value="">Select blood group</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-600 mb-2">Organ to Donate</label>
            <select
              name="organ"
              value={formData.organ}
              onChange={handleChange}
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
            >
              <option value="">Select organ</option>
              <option value="Kidney">Kidney</option>
              <option value="Liver">Liver</option>
              <option value="Heart">Heart</option>
              <option value="Lungs">Lungs</option>
              <option value="Pancreas">Pancreas</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-gray-600 mb-2">Medical History</label>
            <textarea
              name="history"
              value={formData.history}
              onChange={handleChange}
              placeholder="Brief medical history (optional)"
              className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {/* Submit */}
          <div className="md:col-span-2 mt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-500 text-white py-3 rounded-full font-semibold hover:bg-blue-600 disabled:opacity-60"
            >
              {isSubmitting ? "Creating account..." : "Create Account"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
