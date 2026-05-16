import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";
import { getMyDonorProfile, updateMyDonorProfile } from "@/services/donorService";

export default function UserProfile() {
  const { session } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isDonor = session?.role === "donor";

  const [profile, setProfile] = useState({
    name: "",
    phone: "",
    address: "",
    history: "",
  });
  const [isSaving, setIsSaving] = useState(false);

  const { data: donor, isLoading } = useQuery({
    queryKey: ["donor-profile"],
    queryFn: getMyDonorProfile,
    enabled: isDonor,
  });

  useEffect(() => {
    if (session) {
      setProfile((p) => ({ ...p, name: session.fullName }));
    }
  }, [session]);

  useEffect(() => {
    if (donor) {
      setProfile({
        name: session?.fullName || "",
        phone: donor.phone || "",
        address: donor.address || "",
        history: donor.medicalHistory || "No history available",
      });
    }
  }, [donor, session]);

  const handleSave = async () => {
    if (!isDonor) {
      toast.info("Profile updates for this role are coming in Phase 2");
      return;
    }
    setIsSaving(true);
    try {
      await updateMyDonorProfile({
        phone: profile.phone || undefined,
        address: profile.address || undefined,
        medicalHistory: profile.history || undefined,
      });
      await queryClient.invalidateQueries({ queryKey: ["donor-profile"] });
      toast.success("Profile saved");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to save");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-3xl mx-auto px-4">
        <Card className="mb-6">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-2xl font-bold">User Profile</CardTitle>
            <Button variant="outline" onClick={() => navigate(-1)}>
              Back
            </Button>
          </CardHeader>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading && isDonor ? (
              <p className="text-muted-foreground text-sm">Loading profile...</p>
            ) : null}
            <div>
              <Label>Name</Label>
              <Input placeholder="Your full name" value={profile.name} disabled />
            </div>
            <div>
              <Label>Phone Number</Label>
              <Input
                placeholder="Enter phone number"
                value={profile.phone}
                onChange={(e) => setProfile((p) => ({ ...p, phone: e.target.value }))}
              />
            </div>
            <div>
              <Label>Address</Label>
              <Input
                placeholder="City, State, Country"
                value={profile.address}
                onChange={(e) => setProfile((p) => ({ ...p, address: e.target.value }))}
              />
            </div>
            <Button
              className="w-full bg-blue-600 text-white"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </Button>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">History</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{profile.history || "No history available"}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

