import { apiRequest } from "@/lib/api";

export interface DashboardStats {
  totalMatches?: number;
  pendingRequests?: number;
  verifiedDonors?: number;
  nearbyDonors?: number;
  averageCompatibility?: number;
  activeRecipientRequests?: number;
  pendingDonorVerifications?: number;
  pendingRecipientApprovals?: number;
  recentApprovals?: number;
  activeTransplantRequests?: number;
  totalUsers?: number;
  totalDonors?: number;
  totalRecipients?: number;
  totalHospitals?: number;
  flaggedAccounts?: number;
}

export function getDashboardStats(): Promise<DashboardStats> {
  return apiRequest<DashboardStats>("/api/dashboard/stats", { auth: true });
}
