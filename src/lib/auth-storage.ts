const TOKEN_KEY = "livora_token";
const ROLE_KEY = "livora_role";
const USER_ID_KEY = "livora_userId";
const FULL_NAME_KEY = "livora_fullName";

export interface AuthSession {
  token: string;
  role: string;
  userId: string;
  fullName: string;
}

export function saveSession(session: AuthSession): void {
  localStorage.setItem(TOKEN_KEY, session.token);
  localStorage.setItem(ROLE_KEY, session.role);
  localStorage.setItem(USER_ID_KEY, session.userId);
  localStorage.setItem(FULL_NAME_KEY, session.fullName);
}

export function getSession(): AuthSession | null {
  const token = localStorage.getItem(TOKEN_KEY);
  const role = localStorage.getItem(ROLE_KEY);
  const userId = localStorage.getItem(USER_ID_KEY);
  const fullName = localStorage.getItem(FULL_NAME_KEY);
  if (!token || !role || !userId) return null;
  return {
    token,
    role,
    userId,
    fullName: fullName || "",
  };
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(ROLE_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(FULL_NAME_KEY);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
