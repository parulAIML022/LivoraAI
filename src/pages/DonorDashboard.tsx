import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Heart,
  Upload,
  History,
  Settings,
  Menu,
  X,
  Bell,
  FileText,
  LogOut,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import DashboardNotificationBell from "@/components/DashboardNotificationBell";
import DashboardUserNav from "@/components/DashboardUserNav";
import { useDashboardSession } from "@/hooks/useDashboardSession";
import { useLogout } from "@/hooks/useLogout";
import { capitalizeStatus } from "@/lib/userDisplay";
import { ApiError } from "@/lib/api";
import {
  getMyDonorProfile,
  updateMyDonorProfile,
  uploadDonorDocument,
  type DonorProfile,
} from "@/services/donorService";

const DonorDashboard = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const handleLogout = useLogout();
  const { fullName, roleLabel } = useDashboardSession();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("donate");
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [donateForm, setDonateForm] = useState({
    bloodGroup: "",
    organInput: "",
    age: "",
    gender: "",
    address: "",
    phone: "",
    medicalHistory: "",
  });

  const { data: donor, isLoading, error } = useQuery({
    queryKey: ["donor-profile"],
    queryFn: getMyDonorProfile,
  });

  useEffect(() => {
    if (donor) {
      setDonateForm({
        bloodGroup: donor.bloodGroup || "",
        organInput: donor.organs?.join(", ") || "",
        age: donor.age != null ? String(donor.age) : "",
        gender: donor.gender || "",
        address: donor.address || "",
        phone: donor.phone || "",
        medicalHistory: donor.medicalHistory || "",
      });
    }
  }, [donor]);

  const goToProfile = () => navigate("/profile");

  const sidebarItems = [
    { id: "donate", label: "Donate Organ", icon: Upload },
    { id: "history", label: "Donation History", icon: History },
    { id: "profile", label: "Profile & Settings", icon: Settings },
  ];

  const handleDonateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const organs = donateForm.organInput
        .split(",")
        .map((o) => o.trim().toLowerCase())
        .filter(Boolean);

      await updateMyDonorProfile({
        bloodGroup: donateForm.bloodGroup || undefined,
        organs: organs.length ? organs : undefined,
        age: donateForm.age ? Number(donateForm.age) : undefined,
        gender: donateForm.gender || undefined,
        address: donateForm.address || undefined,
        phone: donateForm.phone || undefined,
        medicalHistory: donateForm.medicalHistory || undefined,
      });
      await queryClient.invalidateQueries({ queryKey: ["donor-profile"] });
      toast.success("Donor profile updated successfully");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to save profile");
    } finally {
      setIsSaving(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploading(true);
    try {
      await uploadDonorDocument(file);
      await queryClient.invalidateQueries({ queryKey: ["donor-profile"] });
      toast.success("Document uploaded");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
      e.target.value = "";
    }
  };

  const renderSidebar = (mobile = false) =>
    sidebarItems.map((item) => {
      const Icon = item.icon;
      return (
        <Button
          key={item.id}
          variant={activeTab === item.id ? "default" : "ghost"}
          className="w-full justify-start"
          onClick={() => {
            setActiveTab(item.id);
            if (mobile) setIsMobileMenuOpen(false);
            if (item.id === "profile") goToProfile();
          }}
        >
          <Icon className="h-4 w-4 mr-3" />
          {item.label}
        </Button>
      );
    });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading your donor dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-destructive">
          {error instanceof ApiError ? error.message : "Failed to load donor profile"}
        </p>
        <Button onClick={() => queryClient.invalidateQueries({ queryKey: ["donor-profile"] })}>
          Retry
        </Button>
      </div>
    );
  }

  const profile = donor as DonorProfile;

  return (
    <div className="min-h-screen bg-background flex">
      <aside className="hidden md:block w-64 bg-white border-r border-border min-h-screen p-4 space-y-2">
        {renderSidebar()}
        <Button
          className="w-full mt-4 bg-blue-600 text-white hover:bg-blue-700"
          onClick={() => void handleLogout()}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Log out
        </Button>
      </aside>

      <div className="flex-1">
        <header className="bg-white border-b sticky top-0 z-50 flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X /> : <Menu />}
            </Button>
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 p-2 rounded-lg">
              <Heart className="text-white h-6 w-6" />
            </div>
            <span className="text-xl font-bold text-primary">Livora Donor</span>
          </div>

          <div className="flex items-center space-x-3">
            <DashboardNotificationBell />
            <DashboardUserNav onProfileClick={goToProfile} />
          </div>
        </header>

        {isMobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-40">
            <div
              className="fixed inset-0 bg-black/50"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <aside className="fixed left-0 top-0 w-64 bg-white border-r border-border h-full p-4 space-y-2 pt-16">
              {renderSidebar(true)}
            </aside>
          </div>
        )}

        <main className="p-6 space-y-6">
          <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
            <CardContent className="p-6 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold text-primary mb-2">
                    Welcome, {fullName || "Donor"}! 👋
                  </h1>
                  <p className="text-muted-foreground">
                    {roleLabel} · Profile {profile.profileCompletion}% complete
                    {profile.organs.length > 0
                      ? ` · Registered: ${profile.organs.join(", ")}`
                      : ""}
                  </p>
                </div>
                <Badge variant="secondary">
                  Status: {capitalizeStatus(profile.status)}
                </Badge>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Profile completion</span>
                  <span className="font-medium">{profile.profileCompletion}%</span>
                </div>
                <Progress value={profile.profileCompletion} />
              </div>
            </CardContent>
          </Card>

          {activeTab === "donate" && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Upload className="h-5 w-5" />
                    <span>Donor registration details</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleDonateSubmit} className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label>Blood group</Label>
                        <Input
                          placeholder="e.g. O+"
                          value={donateForm.bloodGroup}
                          onChange={(e) =>
                            setDonateForm((f) => ({ ...f, bloodGroup: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <Label>Organs (comma-separated)</Label>
                        <Input
                          placeholder="kidney, liver"
                          value={donateForm.organInput}
                          onChange={(e) =>
                            setDonateForm((f) => ({ ...f, organInput: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <Label>Age</Label>
                        <Input
                          type="number"
                          placeholder="Age"
                          value={donateForm.age}
                          onChange={(e) =>
                            setDonateForm((f) => ({ ...f, age: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <Label>Gender</Label>
                        <Input
                          placeholder="Gender"
                          value={donateForm.gender}
                          onChange={(e) =>
                            setDonateForm((f) => ({ ...f, gender: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <Label>Phone</Label>
                        <Input
                          value={donateForm.phone}
                          onChange={(e) =>
                            setDonateForm((f) => ({ ...f, phone: e.target.value }))
                          }
                        />
                      </div>
                      <div>
                        <Label>Address / City</Label>
                        <Input
                          value={donateForm.address}
                          onChange={(e) =>
                            setDonateForm((f) => ({ ...f, address: e.target.value }))
                          }
                        />
                      </div>
                    </div>
                    <div>
                      <Label>Medical history</Label>
                      <Input
                        value={donateForm.medicalHistory}
                        onChange={(e) =>
                          setDonateForm((f) => ({ ...f, medicalHistory: e.target.value }))
                        }
                      />
                    </div>
                    <Button
                      type="submit"
                      className="w-full bg-blue-600 text-white"
                      disabled={isSaving}
                    >
                      {isSaving ? "Saving..." : "Save donor profile"}
                    </Button>
                  </form>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Medical documents</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                    disabled={isUploading}
                  />
                  <p className="text-xs text-muted-foreground">
                    PDF, JPG, or PNG up to 10MB
                  </p>
                  {profile.documents.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No documents uploaded yet.</p>
                  ) : (
                    <ul className="space-y-2">
                      {profile.documents.map((doc) => (
                        <li
                          key={doc.filename}
                          className="flex items-center justify-between text-sm border rounded-md p-2"
                        >
                          <span>{doc.originalName}</span>
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-primary hover:underline"
                          >
                            View
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </>
          )}

          {activeTab === "history" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <History className="h-5 w-5" />
                  <span>Donation status</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Registration status:</span>{" "}
                  <span className="capitalize">{profile.status}</span>
                </p>
                <p className="text-sm text-muted-foreground">
                  Organs registered:{" "}
                  {profile.organs.length > 0 ? profile.organs.join(", ") : "None yet"}
                </p>
                <p className="text-sm text-muted-foreground">
                  Member since: {new Date(profile.createdAt).toLocaleDateString()}
                </p>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
};

export default DonorDashboard;


