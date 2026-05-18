/** Display label for API role (coordinator UI maps to admin). */
export function getRoleLabel(role: string | undefined): string {
  switch (role) {
    case "donor":
      return "Organ Donor";
    case "recipient":
      return "Organ Recipient";
    case "hospital":
      return "Hospital";
    case "admin":
      return "Coordinator";
    default:
      return role ? role.charAt(0).toUpperCase() + role.slice(1) : "User";
  }
}

export function getInitials(fullName: string): string {
  return fullName
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "U";
}

export function capitalizeStatus(status: string | undefined): string {
  if (!status) return "Pending";
  return status.charAt(0).toUpperCase() + status.slice(1);
}
