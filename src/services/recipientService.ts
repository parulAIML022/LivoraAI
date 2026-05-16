import { apiRequest } from "@/lib/api";

export interface RecipientProfile {
  id: string;
  userId: string;
  organNeeded?: string | null;
  organs: string[];
  bloodGroup?: string | null;
  age?: number | null;
  gender?: string | null;
  phone?: string | null;
  address?: string | null;
  medicalHistory?: string | null;
  status: string;
  profileCompletion: number;
  createdAt: string;
  updatedAt: string;
}

export interface RecipientUpdatePayload {
  organNeeded?: string;
  organs?: string[];
  bloodGroup?: string;
  age?: number;
  gender?: string;
  phone?: string;
  address?: string;
  medicalHistory?: string;
}

export function getMyRecipientProfile(): Promise<RecipientProfile> {
  return apiRequest<RecipientProfile>("/api/recipients/me", { auth: true });
}

export function updateMyRecipientProfile(
  payload: RecipientUpdatePayload
): Promise<RecipientProfile> {
  return apiRequest<RecipientProfile>("/api/recipients/me", {
    method: "PUT",
    auth: true,
    body: payload,
  });
}
