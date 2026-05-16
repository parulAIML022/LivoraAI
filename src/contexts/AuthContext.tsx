import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  clearSession,
  getSession,
  saveSession,
  type AuthSession,
} from "@/lib/auth-storage";
import {
  getMe,
  login as apiLogin,
  logout as apiLogout,
  signup as apiSignup,
  tokenToSession,
  type LoginPayload,
  type SignupPayload,
} from "@/services/authService";
import { ApiError } from "@/lib/api";

interface AuthContextValue {
  session: AuthSession | null;
  isLoading: boolean;
  login: (payload: LoginPayload, expectedRole?: string) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(() => getSession());
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const current = getSession();
    if (!current?.token) {
      setSession(null);
      return;
    }
    try {
      const user = await getMe();
      const updated: AuthSession = {
        ...current,
        fullName: user.fullName,
        role: user.role,
        userId: user.userId,
      };
      saveSession(updated);
      setSession(updated);
    } catch {
      clearSession();
      setSession(null);
    }
  }, []);

  useEffect(() => {
    refreshUser().finally(() => setIsLoading(false));
  }, [refreshUser]);

  const login = useCallback(
    async (payload: LoginPayload, expectedRole?: string) => {
      const data = await apiLogin(payload);
      const apiRole = data.role;
      if (expectedRole) {
        const normalized = expectedRole === "coordinator" ? "admin" : expectedRole;
        if (apiRole !== normalized) {
          throw new ApiError(
            `This account is registered as ${apiRole}, not ${expectedRole}.`,
            403
          );
        }
      }
      const next = tokenToSession(data);
      saveSession(next);
      setSession(next);
    },
    []
  );

  const signup = useCallback(async (payload: SignupPayload) => {
    const data = await apiSignup(payload);
    const next = tokenToSession(data);
    saveSession(next);
    setSession(next);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      /* token may already be invalid */
    }
    clearSession();
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({
      session,
      isLoading,
      login,
      signup,
      logout,
      refreshUser,
    }),
    [session, isLoading, login, signup, logout, refreshUser]
  );

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

/** Dashboard path for a stored API role */
export function dashboardPathForRole(role: string): string {
  switch (role) {
    case "donor":
      return "/donor-dashboard";
    case "recipient":
      return "/recipient-dashboard";
    case "hospital":
      return "/hospital-dashboard";
    case "admin":
      return "/coordinator-dashboard";
    default:
      return "/";
  }
}
