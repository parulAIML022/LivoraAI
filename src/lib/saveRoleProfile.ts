import { updateMyDonorProfile } from "@/services/donorService";
import { updateMyRecipientProfile } from "@/services/recipientService";
import { toApiRole } from "@/services/authService";

type SignUpFormData = {
  phone: string;
  location: string;
  bloodGroup: string;
  organType: string;
  medicalHistory: string;
  hospitalName: string;
};

/**
 * After auth signup, persist role-specific fields via profile APIs (not /auth/signup).
 */
export async function saveRoleProfileAfterSignup(
  role: string,
  form: SignUpFormData
): Promise<void> {
  const apiRole = toApiRole(role);

  if (apiRole === "donor") {
    const organs = form.organType ? [form.organType.toLowerCase()] : undefined;
    const hasProfile =
      form.phone ||
      form.location ||
      form.bloodGroup ||
      form.organType ||
      form.medicalHistory;
    if (!hasProfile) return;

    await updateMyDonorProfile({
      phone: form.phone || undefined,
      address: form.location || undefined,
      bloodGroup: form.bloodGroup || undefined,
      organs,
      medicalHistory: form.medicalHistory || undefined,
    });
    return;
  }

  if (apiRole === "recipient") {
    const hasProfile =
      form.phone ||
      form.location ||
      form.bloodGroup ||
      form.organType ||
      form.medicalHistory;
    if (!hasProfile) return;

    await updateMyRecipientProfile({
      phone: form.phone || undefined,
      address: form.location || undefined,
      bloodGroup: form.bloodGroup || undefined,
      organNeeded: form.organType || undefined,
      organs: form.organType ? [form.organType.toLowerCase()] : undefined,
      medicalHistory: form.medicalHistory || undefined,
    });
  }

  // hospital / admin: profile APIs in later phases
}
