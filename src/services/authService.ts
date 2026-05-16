import { apiRequest } from "@/lib/api";
import type { AuthSession } from "@/lib/auth-storage";

export interface TokenResponse {
  access_token: string;
  token_type: string;
  userId: string;
  role: string;
  fullName: string;
}

export interface SignupPayload {
  fullName: string;
  email: string;
  password: string;
  role: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

/** Map UI role names to API roles */
export function toApiRole(role: string): string {
  if (role === "coordinator") return "admin";
  return role;
}

export function tokenToSession(data: TokenResponse): AuthSession {
  return {
    token: data.access_token,
    role: data.role,
    userId: data.userId,
    fullName: data.fullName,
  };
}

export function signup(payload: SignupPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/api/auth/signup", {
    method: "POST",
    body: {
      fullName: payload.fullName,
      email: payload.email,
      password: payload.password,
      role: toApiRole(payload.role),
    },
  });
}

export function login(payload: LoginPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: payload,
  });
}

export function logout(): Promise<{ message: string }> {
  return apiRequest<{ message: string }>("/api/auth/logout", {
    method: "POST",
    auth: true,
  });
}

export function getMe(): Promise<{
  userId: string;
  fullName: string;
  email: string;
  role: string;
  createdAt: string;
}> {
  return apiRequest("/api/auth/me", { auth: true });
}
