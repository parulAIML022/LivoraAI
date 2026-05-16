import { apiRequest } from "@/lib/api";

export interface DonorDocument {
  filename: string;
  originalName: string;
  contentType: string;
  uploadedAt: string;
  url: string;
}

export interface DonorProfile {
  id: string;
  userId: string;
  bloodGroup?: string | null;
  organs: string[];
  age?: number | null;
  gender?: string | null;
  phone?: string | null;
  address?: string | null;
  medicalHistory?: string | null;
  documents: DonorDocument[];
  status: string;
  profileCompletion: number;
  createdAt: string;
  updatedAt: string;
}

export interface DonorUpdatePayload {
  bloodGroup?: string;
  organs?: string[];
  age?: number;
  gender?: string;
  phone?: string;
  address?: string;
  medicalHistory?: string;
}

export function getMyDonorProfile(): Promise<DonorProfile> {
  return apiRequest<DonorProfile>("/api/donors/me", { auth: true });
}

export function updateMyDonorProfile(
  payload: DonorUpdatePayload
): Promise<DonorProfile> {
  return apiRequest<DonorProfile>("/api/donors/me", {
    method: "PUT",
    auth: true,
    body: payload,
  });
}

export function uploadDonorDocument(file: File): Promise<DonorProfile> {
  const form = new FormData();
  form.append("file", file);
  return apiRequest<DonorProfile>("/api/donors/me/documents", {
    method: "POST",
    auth: true,
    body: form,
  });
}
