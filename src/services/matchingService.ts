import { apiRequest } from "@/lib/api";

export interface MatchSuggestion {
  id: string;
  counterpartUserId: string;
  displayName: string;
  initials: string;
  bloodGroup?: string | null;
  compatibility: number;
  location: string;
  distance: string;
  distanceKm: number;
  urgency: string;
  organType?: string | null;
  verificationStatus: string;
  role: string;
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

export interface UrgentAlert {
  message: string;
  location?: string | null;
  matchId?: string | null;
}

export interface MatchingResponse {
  matches: MatchSuggestion[];
  stats: MatchStats;
  urgentAlert?: UrgentAlert | null;
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
