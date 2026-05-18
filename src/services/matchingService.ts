import { apiRequest } from "@/lib/api";

export interface DonorMatch {
  donorName: string;
  bloodGroup?: string | null;
  organ?: string | null;
  location?: string | null;
  status: string;
  compatibilityScore: number;
}

export interface MatchStats {
  totalMatches: number;
  nearbyMatches: number;
  averageCompatibility: number;
  newMatchesThisWeek: number;
  pendingRequests?: number;
  verifiedDonors?: number;
  activeRecipientRequests?: number;
}

export interface MatchingResponse {
  matches: DonorMatch[];
  message?: string | null;
  stats: MatchStats;
}

export function getMyMatches(): Promise<MatchingResponse> {
  return apiRequest<MatchingResponse>("/api/matching/me", { auth: true });
}

export function getRecipientMatches(): Promise<MatchingResponse> {
  return apiRequest<MatchingResponse>("/api/matching/recipient", { auth: true });
}

export function getDonorMatches(): Promise<MatchingResponse> {
  return apiRequest<MatchingResponse>("/api/matching/donor", { auth: true });
}
