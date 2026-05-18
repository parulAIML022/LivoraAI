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
  type AuthUser,
  type LoginPayload,
  type SignupPayload,
} from "@/services/authService";
import { ApiError } from "@/lib/api";

interface AuthContextValue {
  user: AuthUser | null;
  session: AuthSession | null;
  isLoading: boolean;
  login: (payload: LoginPayload, expectedRole?: string) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function sessionFromUser(user: AuthUser, token: string): AuthSession {
  return {
    token,
    role: user.role,
    userId: user.userId,
    fullName: user.fullName,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(() => getSession());
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const current = getSession();
    if (!current?.token) {
      setUser(null);
      setSession(null);
      return;
    }
    try {
      const me = await getMe();
      setUser(me);
      const updated = sessionFromUser(me, current.token);
      saveSession(updated);
      setSession(updated);
    } catch {
      clearSession();
      setUser(null);
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
      const me = await getMe();
      setUser(me);
      saveSession(sessionFromUser(me, next.token));
      setSession(sessionFromUser(me, next.token));
    },
    []
  );

  const signup = useCallback(async (payload: SignupPayload) => {
    const data = await apiSignup(payload);
    const next = tokenToSession(data);
    saveSession(next);
    setSession(next);
    const me = await getMe();
    setUser(me);
    const synced = sessionFromUser(me, next.token);
    saveSession(synced);
    setSession(synced);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      /* token may already be invalid */
    }
    clearSession();
    setUser(null);
    setSession(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      session,
      isLoading,
      login,
      signup,
      logout,
      refreshUser,
    }),
    [user, session, isLoading, login, signup, logout, refreshUser]
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
