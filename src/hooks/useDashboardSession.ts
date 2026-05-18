import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getInitials, getRoleLabel } from "@/lib/userDisplay";

/**
 * Ensures /api/auth/me is loaded for dashboard views and exposes display helpers.
 */
export function useDashboardSession() {
  const { user, session, isLoading, refreshUser } = useAuth();

  useEffect(() => {
    if (session?.token) {
      refreshUser();
    }
  }, [session?.token, refreshUser]);

  const fullName = user?.fullName ?? session?.fullName ?? "";
  const role = user?.role ?? session?.role ?? "";
  const email = user?.email ?? "";

  return {
    user,
    session,
    isLoading,
    fullName,
    email,
    role,
    roleLabel: getRoleLabel(role),
    initials: getInitials(fullName),
    refreshUser,
  };
}
