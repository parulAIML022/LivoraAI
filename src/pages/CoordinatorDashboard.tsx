import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  Users,
  Activity,
  ClipboardList,
  Settings,
  Menu,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import DashboardNotificationBell from "@/components/DashboardNotificationBell";
import DashboardUserNav from "@/components/DashboardUserNav";
import { useDashboardSession } from "@/hooks/useDashboardSession";
import { ApiError } from "@/lib/api";
import { capitalizeStatus } from "@/lib/userDisplay";
import {
  getAdminStats,
  getPendingUsers,
  updateDonorStatus,
  updateRecipientStatus,
} from "@/services/adminService";

const CoordinatorDashboard = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { fullName, roleLabel } = useDashboardSession();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("home");

  const { data: stats } = useQuery({
    queryKey: ["admin-stats"],
    queryFn: getAdminStats,
  });

  const { data: pending } = useQuery({
    queryKey: ["admin-pending"],
    queryFn: () => getPendingUsers("pending"),
    enabled: activeTab === "users",
  });

  const statusMutation = useMutation({
    mutationFn: async ({
      userId,
      role,
      status,
    }: {
      userId: string;
      role: string;
      status: "verified" | "active" | "inactive";
    }) => {
      if (role === "donor") {
        return updateDonorStatus(userId, status);
      }
      return updateRecipientStatus(userId, status);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-pending"] });
      queryClient.invalidateQueries({ queryKey: ["admin-stats"] });
      queryClient.invalidateQueries({ queryKey: ["matching-me"] });
      queryClient.invalidateQueries({ queryKey: ["recipient-matches"] });
      queryClient.invalidateQueries({ queryKey: ["donor-matches"] });
      toast.success("Status updated");
    },
    onError: (err) => {
      toast.error(err instanceof ApiError ? err.message : "Update failed");
    },
  });

  const goToProfile = () => navigate("/profile");

  const sidebarItems = [
    { id: "home", label: "Dashboard Home", icon: Users },
    { id: "active", label: "Active Transplants", icon: Activity },
    { id: "users", label: "User Management", icon: ClipboardList },
    { id: "profile", label: "Profile & Settings", icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      <aside className="hidden md:block w-64 bg-white border-r border-border min-h-screen p-4 space-y-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.id}
              variant={activeTab === item.id ? "default" : "ghost"}
              className="w-full justify-start"
              onClick={() => {
                setActiveTab(item.id);
                if (item.id === "profile") goToProfile();
              }}
            >
              <Icon className="h-4 w-4 mr-3" />
              {item.label}
            </Button>
          );
        })}
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
              <Users className="text-white h-6 w-6" />
            </div>
            <span className="text-xl font-bold text-primary">Coordinator Panel</span>
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
            <aside className="fixed left-0 top-0 w-64 bg-white border-r border-border h-full p-4 pt-16 space-y-2">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Button
                    key={item.id}
                    variant={activeTab === item.id ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => {
                      setActiveTab(item.id);
                      setIsMobileMenuOpen(false);
                      if (item.id === "profile") goToProfile();
                    }}
                  >
                    <Icon className="h-4 w-4 mr-3" />
                    {item.label}
                  </Button>
                );
              })}
            </aside>
          </div>
        )}

        <main className="p-6 space-y-6">
          <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
            <CardContent className="p-6">
              <h1 className="text-2xl font-bold text-primary mb-2">
                Welcome, {fullName || "Coordinator"}
              </h1>
              <p className="text-muted-foreground">
                {roleLabel} — manage organ matching, donor–recipient coordination, and the
                hospital network.
              </p>
            </CardContent>
          </Card>

          {activeTab === "home" && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs text-muted-foreground">Total users</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{stats?.totalUsers ?? 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs text-muted-foreground">Donors</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{stats?.totalDonors ?? 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs text-muted-foreground">Recipients</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{stats?.totalRecipients ?? 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs text-muted-foreground">Hospitals</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">{stats?.totalHospitals ?? 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs text-muted-foreground">Flagged</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold text-destructive">
                      {stats?.flaggedAccounts ?? 0}
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Users className="h-5 w-5" />
                    <span>Dashboard Overview</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>
                    Pending verifications:{" "}
                    {(stats?.pendingDonorVerifications ?? 0) +
                      (stats?.pendingRecipientApprovals ?? 0)}
                  </p>
                  <p>Platform matches: {stats?.totalMatches ?? 0}</p>
                  <p>Active transplant requests: {stats?.activeTransplantRequests ?? 0}</p>
                  <p>Recent approvals (7 days): {stats?.recentApprovals ?? 0}</p>
                </CardContent>
              </Card>
            </>
          )}

          {activeTab === "active" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="h-5 w-5" />
                  <span>Active Transplants</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-3">
                  {stats?.activeTransplantRequests ?? 0} active recipient request(s) across the
                  network.
                </p>
                <Button
                  className="w-full bg-blue-600 text-white"
                  onClick={() => setActiveTab("users")}
                >
                  Review pending registrations
                </Button>
              </CardContent>
            </Card>
          )}

          {activeTab === "users" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <ClipboardList className="h-5 w-5" />
                  <span>User Management</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <section>
                  <h3 className="text-sm font-semibold mb-3">Donors awaiting approval</h3>
                  {(pending?.donors ?? []).length === 0 ? (
                    <p className="text-sm text-muted-foreground">No pending donors.</p>
                  ) : (
                    <ul className="space-y-3">
                      {pending?.donors.map((d) => (
                        <li
                          key={d.userId}
                          className="flex flex-wrap justify-between gap-2 border rounded-md p-3"
                        >
                          <div>
                            <p className="font-medium">{d.fullName}</p>
                            <p className="text-xs text-muted-foreground">{d.email}</p>
                            <Badge variant="secondary" className="mt-1">
                              {capitalizeStatus(d.profileStatus ?? "pending")}
                            </Badge>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              disabled={statusMutation.isPending}
                              onClick={() =>
                                statusMutation.mutate({
                                  userId: d.userId,
                                  role: "donor",
                                  status: "verified",
                                })
                              }
                            >
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={statusMutation.isPending}
                              onClick={() =>
                                statusMutation.mutate({
                                  userId: d.userId,
                                  role: "donor",
                                  status: "inactive",
                                })
                              }
                            >
                              Reject
                            </Button>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </section>

                <section>
                  <h3 className="text-sm font-semibold mb-3">Recipients awaiting approval</h3>
                  {(pending?.recipients ?? []).length === 0 ? (
                    <p className="text-sm text-muted-foreground">No pending recipients.</p>
                  ) : (
                    <ul className="space-y-3">
                      {pending?.recipients.map((r) => (
                        <li
                          key={r.userId}
                          className="flex flex-wrap justify-between gap-2 border rounded-md p-3"
                        >
                          <div>
                            <p className="font-medium">{r.fullName}</p>
                            <p className="text-xs text-muted-foreground">{r.email}</p>
                            <Badge variant="secondary" className="mt-1">
                              {capitalizeStatus(r.profileStatus ?? "pending")}
                            </Badge>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              disabled={statusMutation.isPending}
                              onClick={() =>
                                statusMutation.mutate({
                                  userId: r.userId,
                                  role: "recipient",
                                  status: "active",
                                })
                              }
                            >
                              Approve (active)
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={statusMutation.isPending}
                              onClick={() =>
                                statusMutation.mutate({
                                  userId: r.userId,
                                  role: "recipient",
                                  status: "inactive",
                                })
                              }
                            >
                              Reject
                            </Button>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
};

export default CoordinatorDashboard;

