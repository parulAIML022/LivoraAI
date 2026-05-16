import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useAuth, dashboardPathForRole } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";
import { toApiRole } from "@/services/authService";
import { saveRoleProfileAfterSignup } from "@/lib/saveRoleProfile";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Heart, User, Building, UserCog, Stethoscope } from "lucide-react";

type UserRole = "donor" | "recipient" | "hospital" | "coordinator";

const SignUp = () => {
  const [selectedRole, setSelectedRole] = useState<UserRole | "">("");
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    phone: "",
    location: "",
    bloodGroup: "",
    organType: "",
    hospitalName: "",
    address: "",
    icuCapacity: "",
    medicalHistory: "",
  });

  const navigate = useNavigate();
  const { signup, session, isLoading: authLoading } = useAuth();

  useEffect(() => {
    if (!authLoading && session) {
      navigate(dashboardPathForRole(session.role), { replace: true });
    }
  }, [authLoading, session, navigate]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const roles = [
    { id: "donor" as UserRole, title: "Organ Donor", description: "Register to save lives by donating organs", icon: Heart, color: "from-cyan-400 to-blue-500" },
    { id: "recipient" as UserRole, title: "Organ Recipient", description: "Find a matching organ donor for treatment", icon: User, color: "from-blue-400 to-blue-600" },
    { id: "hospital" as UserRole, title: "Hospital", description: "Institutional registration for medical facilities", icon: Building, color: "from-blue-500 to-cyan-500" },
    { id: "coordinator" as UserRole, title: "Coordinator", description: "Facilitate organ donation and matching process", icon: UserCog, color: "from-cyan-500 to-blue-400" },
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedRole) {
      toast.error("Please select a role");
      return;
    }
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
        fullName: formData.name,
        email: formData.email,
        password: formData.password,
        role: selectedRole,
      });
      await saveRoleProfileAfterSignup(selectedRole, formData);
      toast.success("Account created successfully");
      const apiRole = toApiRole(selectedRole);
      navigate(dashboardPathForRole(apiRole));
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Registration failed. Please try again.";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderRoleSpecificFields = () => {
    switch (selectedRole) {
      case "donor":
        return (
          <div className="space-y-4 animate-fade-in">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Blood Group *</Label>
                <Select onValueChange={(value) => handleInputChange("bloodGroup", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select blood group" />
                  </SelectTrigger>
                  <SelectContent>
                    {["A+","A-","B+","B-","AB+","AB-","O+","O-"].map(bg => (
                      <SelectItem key={bg} value={bg}>{bg}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Organ to Donate *</Label>
                <Select onValueChange={(value) => handleInputChange("organType", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select organ" />
                  </SelectTrigger>
                  <SelectContent>
                    {["Kidney","Liver","Heart","Lungs","Pancreas","Cornea"].map(org => (
                      <SelectItem key={org} value={org.toLowerCase()}>{org}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Medical History</Label>
              <Textarea
                placeholder="Brief medical history (optional)"
                value={formData.medicalHistory}
                onChange={(e) => handleInputChange("medicalHistory", e.target.value)}
              />
            </div>
          </div>
        );

      case "recipient":
        return (
          <div className="space-y-4 animate-fade-in">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label>Organ Needed *</Label>
                <Select onValueChange={(value) => handleInputChange("organType", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select organ" />
                  </SelectTrigger>
                  <SelectContent>
                    {["Kidney","Liver","Heart","Lungs","Pancreas","Cornea"].map(org => (
                      <SelectItem key={org} value={org.toLowerCase()}>{org}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Blood Group *</Label>
                <Select onValueChange={(value) => handleInputChange("bloodGroup", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select blood group" />
                  </SelectTrigger>
                  <SelectContent>
                    {["A+","A-","B+","B-","AB+","AB-","O+","O-"].map(bg => (
                      <SelectItem key={bg} value={bg}>{bg}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Medical History *</Label>
              <Textarea
                placeholder="Detailed medical history"
                value={formData.medicalHistory}
                onChange={(e) => handleInputChange("medicalHistory", e.target.value)}
                required
              />
            </div>
          </div>
        );

      case "hospital":
        return (
          <div className="space-y-4 animate-fade-in">
            <div>
              <Label>Hospital Name *</Label>
              <Input
                placeholder="Enter hospital name"
                value={formData.hospitalName}
                onChange={(e) => handleInputChange("hospitalName", e.target.value)}
                required
              />
            </div>
            <div>
              <Label>Hospital Address *</Label>
              <Textarea
                placeholder="Complete hospital address"
                value={formData.address}
                onChange={(e) => handleInputChange("address", e.target.value)}
                required
              />
            </div>
            <div>
              <Label>ICU Capacity</Label>
              <Input
                type="number"
                placeholder="Number of ICU beds"
                value={formData.icuCapacity}
                onChange={(e) => handleInputChange("icuCapacity", e.target.value)}
              />
            </div>
          </div>
        );

      case "coordinator":
        return (
          <div className="space-y-4 animate-fade-in">
            <div>
              <Label>Organization / Institution *</Label>
              <Input
                placeholder="Enter organization name"
                value={formData.hospitalName}
                onChange={(e) => handleInputChange("hospitalName", e.target.value)}
                required
              />
            </div>
            <div>
              <Label>Experience & Qualifications</Label>
              <Textarea
                placeholder="Describe your experience in organ donation coordination"
                value={formData.medicalHistory}
                onChange={(e) => handleInputChange("medicalHistory", e.target.value)}
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text mb-4">
            Join the LivoraAI Community
          </h1>
          <p className="text-lg text-gray-600">Choose your role and start saving lives today</p>
        </div>

        {!selectedRole ? (
          <div className="grid md:grid-cols-2 gap-6">
            {roles.map((role) => {
              const Icon = role.icon;
              return (
                <Card
                  key={role.id}
                  className="cursor-pointer hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                  onClick={() => setSelectedRole(role.id)}
                >
                  <CardHeader className="text-center">
                    <div className={`bg-gradient-to-r ${role.color} p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center`}>
                      <Icon className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl">{role.title}</CardTitle>
                    <CardDescription>{role.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="text-center">
                    <Button className="bg-gradient-to-r from-blue-500 to-cyan-500 w-full text-white font-semibold rounded-xl">
                      Select Role
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card className="shadow-xl animate-fade-in">
            <CardHeader className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className={`bg-gradient-to-r ${roles.find((r) => r.id === selectedRole)?.color} p-3 rounded-lg`}>
                  {selectedRole === "donor" && <Heart className="h-6 w-6 text-white" />}
                  {selectedRole === "recipient" && <User className="h-6 w-6 text-white" />}
                  {selectedRole === "hospital" && <Building className="h-6 w-6 text-white" />}
                  {selectedRole === "coordinator" && <UserCog className="h-6 w-6 text-white" />}
                </div>
                <div>
                  <CardTitle>{roles.find((r) => r.id === selectedRole)?.title}</CardTitle>
                  <CardDescription>Fill out the form below to register</CardDescription>
                </div>
              </div>
              <Button variant="outline" onClick={() => setSelectedRole("")}>Change Role</Button>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Common Fields */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Full Name *</Label>
                    <Input
                      placeholder="Enter your full name"
                      value={formData.name}
                      onChange={(e) => handleInputChange("name", e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label>Email *</Label>
                    <Input
                      type="email"
                      placeholder="Enter your email"
                      value={formData.email}
                      onChange={(e) => handleInputChange("email", e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Password *</Label>
                    <Input
                      type="password"
                      placeholder="Create password"
                      value={formData.password}
                      onChange={(e) => handleInputChange("password", e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label>Confirm Password *</Label>
                    <Input
                      type="password"
                      placeholder="Confirm password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label>Phone Number *</Label>
                    <Input
                      type="tel"
                      placeholder="Enter your phone number"
                      value={formData.phone}
                      onChange={(e) => handleInputChange("phone", e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label>Location *</Label>
                    <Input
                      placeholder="City, State, Country"
                      value={formData.location}
                      onChange={(e) => handleInputChange("location", e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Role Specific Fields */}
                {renderRoleSpecificFields()}

                <div className="flex flex-col sm:flex-row gap-4 pt-6">
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="bg-gradient-to-r from-blue-500 to-cyan-500 flex-1 text-white font-semibold py-3 rounded-xl hover:shadow-lg"
                  >
                    {isSubmitting ? "Creating account..." : "Create Account"}
                    <Stethoscope className="ml-2 h-5 w-5" />
                  </Button>
                </div>

                <div className="text-center pt-4 border-t border-gray-200">
                  <p className="text-gray-600">
                    Already have an account?{" "}
                    <Link to="/signin" className="text-blue-600 hover:text-blue-700 font-medium">
                      Sign In
                    </Link>
                  </p>
                </div>
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default SignUp;
