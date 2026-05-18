import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import DashboardNotificationBell from "@/components/DashboardNotificationBell";
import DashboardUserNav from "@/components/DashboardUserNav";
import { useDashboardSession } from "@/hooks/useDashboardSession";
import { capitalizeStatus, getInitials } from "@/lib/userDisplay";
import { getMyMatches } from "@/services/matchingService";
import { getNotifications } from "@/services/notificationService";
import { getMyRecipientProfile } from "@/services/recipientService";

import {
  Search,
  Heart,
  Users,
  Activity,
  MapPin,
  MessageCircle,
  Settings,
  Menu,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

function formatNotificationTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${Math.max(mins, 1)}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const { fullName, roleLabel } = useDashboardSession();
  const { data: profile } = useQuery({
    queryKey: ["recipient-profile"],
    queryFn: getMyRecipientProfile,
  });

  const { data: matching } = useQuery({
    queryKey: ["matching-me"],
    queryFn: getMyMatches,
    refetchOnMount: "always",
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => getNotifications(5),
  });

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("home");

  const sidebarItems = [
    { id: "home", label: "Home", icon: Heart },
    { id: "matches", label: "Matches", icon: Users },
    { id: "requests", label: "Requests", icon: Activity },
    { id: "messages", label: "Messages", icon: MessageCircle },
    { id: "tracking", label: "Tracking", icon: MapPin },
    { id: "profile", label: "Profile & Settings", icon: Settings },
  ];

  const matches = matching?.matches ?? [];
  const stats = matching?.stats;
  const noMatchesMessage =
    matching?.message ?? "No compatible donors found.";

  const goToProfile = () => {
    navigate("/profile");
  };

  const organLabel =
    profile?.organNeeded ||
    (profile?.organs?.length ? profile.organs.join(", ") : null) ||
    "organ";

  const isVerified =
    profile?.status === "verified" || profile?.status === "active";

  return (
    <div className="min-h-screen bg-background">

      <header className="bg-white border-b border-border sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>

            <div className="bg-gradient-to-r from-primary to-secondary p-2 rounded-lg">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold text-primary">Livora</span>
          </div>

          <div className="hidden md:flex items-center flex-1 max-w-lg mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input placeholder="Search organs, hospitals..." className="pl-10 bg-muted/30" />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <DashboardNotificationBell />
            <DashboardUserNav onProfileClick={goToProfile} />
          </div>
        </div>
      </header>

      <div className="flex">
        <aside className="hidden md:block w-64 bg-white border-r border-border min-h-screen">
          <nav className="p-4 space-y-2">
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
          </nav>
        </aside>

        {isMobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-40">
            <div
              className="fixed inset-0 bg-black/50"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <aside className="fixed left-0 top-16 w-64 bg-white border-r border-border h-full">
              <nav className="p-4 space-y-2">
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
              </nav>
            </aside>
          </div>
        )}

        <main className="flex-1 p-4 md:p-6">
          <Card className="mb-6 bg-gradient-to-r from-primary/10 to-secondary/10 border-primary/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-primary mb-2">
                    Hi, {fullName || "there"} 👋
                  </h1>
                  <p className="text-muted-foreground mb-2">
                    {roleLabel}
                    {profile
                      ? ` · Waiting for a ${organLabel} match`
                      : " · Complete your profile to improve matching"}
                    {profile?.bloodGroup ? ` · Blood group ${profile.bloodGroup}` : ""}
                  </p>
                  {profile?.status && (
                    <Badge
                      variant="secondary"
                      className={
                        profile.status === "pending"
                          ? "bg-orange-100 text-orange-800 border-orange-200"
                          : ""
                      }
                    >
                      {capitalizeStatus(profile.status)}
                    </Badge>
                  )}
                </div>
                <div className="hidden md:block">
                  <div className="bg-white/80 rounded-full p-4">
                    <Heart className="h-8 w-8 text-primary" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Matches Found
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-primary">
                  {stats?.totalMatches ?? 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  +{stats?.newMatchesThisWeek ?? 0} new this week
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Potential Donors Nearby
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-secondary">
                  {stats?.nearbyMatches ?? 0}
                </div>
                <p className="text-xs text-muted-foreground">Within 50km radius</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Average Match Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-accent">
                  {stats?.averageCompatibility ?? 0}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {(stats?.averageCompatibility ?? 0) >= 80
                    ? "Excellent compatibility"
                    : "Based on live donor data"}
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>AI Match Suggestions</span>
              </CardTitle>
            </CardHeader>

            <CardContent>
              {matches.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">{noMatchesMessage}</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {matches.map((match, index) => (
                    <Card
                      key={`${match.donorName}-${match.organ}-${index}`}
                      className="border border-border/50 hover:shadow-md transition-shadow"
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-secondary text-white">
                              {getInitials(match.donorName)}
                            </AvatarFallback>
                          </Avatar>

                          <Badge variant="secondary" className="capitalize">
                            {match.status}
                          </Badge>
                        </div>

                        <p className="text-sm font-medium mb-2 truncate">
                          {match.donorName}
                        </p>

                        <div className="space-y-2 mb-4">
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Blood Group:</span>
                            <span className="font-semibold">{match.bloodGroup ?? "—"}</span>
                          </div>

                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Organ:</span>
                            <span className="text-sm capitalize">
                              {match.organ ?? "—"}
                            </span>
                          </div>

                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">
                              Compatibility:
                            </span>
                            <span className="font-semibold text-primary">
                              {match.compatibilityScore}%
                            </span>
                          </div>

                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Location:</span>
                            <span className="text-sm">{match.location ?? "—"}</span>
                          </div>

                        </div>

                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            View Details
                          </Button>
                          <Button size="sm" className="flex-1">
                            Request Organ
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </main>

        <aside className="hidden lg:block w-80 bg-white border-l border-border min-h-screen p-4">
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-sm">Recent Messages</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {(notifications?.items ?? []).length === 0 ? (
                <p className="text-xs text-muted-foreground">No notifications yet.</p>
              ) : (
                notifications?.items.map((n) => (
                  <div
                    key={n.id}
                    className="flex items-center space-x-3 p-2 rounded-lg hover:bg-muted/50 cursor-pointer"
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-primary text-white">
                        {getInitials(n.title)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{n.title}</p>
                      <p className="text-xs text-muted-foreground truncate">{n.message}</p>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatNotificationTime(n.createdAt)}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-sm">Verification Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center space-x-2">
                <div
                  className={`h-2 w-2 rounded-full ${
                    profile?.medicalHistory ? "bg-primary" : "bg-orange-500"
                  }`}
                />
                <span className="text-sm">
                  Medical profile {profile?.medicalHistory ? "complete ✓" : "incomplete"}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <div
                  className={`h-2 w-2 rounded-full ${
                    profile?.bloodGroup ? "bg-primary" : "bg-orange-500"
                  }`}
                />
                <span className="text-sm">
                  Blood group {profile?.bloodGroup ? "on file ✓" : "missing"}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <div
                  className={`h-2 w-2 rounded-full ${
                    isVerified ? "bg-primary" : "bg-orange-500"
                  }`}
                />
                <span className="text-sm">
                  Hospital approval{" "}
                  {isVerified ? "verified ✓" : capitalizeStatus(profile?.status ?? "pending")}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Tips & Support</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-xs text-muted-foreground">
                  💡 Keep your medical information updated for better matches.
                </p>
                <Button size="sm" variant="outline" className="w-full">
                  Chat with Support
                </Button>
              </div>
            </CardContent>
          </Card>
        </aside>
      </div>

      <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-border">
        <div className="grid grid-cols-5 gap-1 p-2">
          {sidebarItems.slice(0, 5).map((item) => {
            const Icon = item.icon;
            return (
              <Button
                key={item.id}
                variant="ghost"
                size="sm"
                className={`flex flex-col items-center py-2 h-auto ${
                  activeTab === item.id ? "text-primary" : "text-muted-foreground"
                }`}
                onClick={() => {
                  setActiveTab(item.id);
                  if (item.id === "profile") goToProfile();
                }}
              >
                <Icon className="h-4 w-4 mb-1" />
                <span className="text-xs">{item.label.split(" ")[0]}</span>
              </Button>
            );
          })}
        </div>
      </div>

      <Button
        size="lg"
        className="md:hidden fixed bottom-20 right-4 rounded-full h-14 w-14 shadow-lg"
      >
        <Heart className="h-6 w-6" />
      </Button>
    </div>
  );
};

export default Dashboard;

