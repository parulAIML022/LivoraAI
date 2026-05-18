import { apiRequest } from "@/lib/api";
import type { DashboardStats } from "@/services/dashboardService";

export interface AdminUserSummary {
  userId: string;
  fullName: string;
  email: string;
  role: string;
  profileStatus?: string | null;
  bloodGroup?: string | null;
  organs: string[];
  organNeeded?: string | null;
  createdAt?: string | null;
}

export interface AdminUserListResponse {
  donors: AdminUserSummary[];
  recipients: AdminUserSummary[];
}

export function getAdminStats(): Promise<DashboardStats> {
  return apiRequest<DashboardStats>("/api/admin/stats", { auth: true });
}

export function getPendingUsers(
  status = "pending"
): Promise<AdminUserListResponse> {
  return apiRequest<AdminUserListResponse>(
    `/api/admin/pending?status=${encodeURIComponent(status)}`,
    { auth: true }
  );
}

export function updateDonorStatus(
  userId: string,
  status: "pending" | "verified" | "active" | "inactive"
): Promise<unknown> {
  return apiRequest(`/api/donors/${userId}/status`, {
    method: "PATCH",
    auth: true,
    body: { status },
  });
}

export function updateRecipientStatus(
  userId: string,
  status: "pending" | "verified" | "active" | "inactive"
): Promise<unknown> {
  return apiRequest(`/api/recipients/${userId}/status`, {
    method: "PATCH",
    auth: true,
    body: { status },
  });
}
