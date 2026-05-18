import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";

/** Clears session, cache, and redirects to sign-in (role selection). */
export function useLogout() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useCallback(async () => {
    await logout();
    queryClient.clear();
    navigate("/signin", { replace: true });
  }, [logout, navigate, queryClient]);
}
