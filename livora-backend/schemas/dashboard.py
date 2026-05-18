from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    totalMatches: int = 0
    pendingRequests: int = 0
    verifiedDonors: int = 0
    nearbyDonors: int = 0
    averageCompatibility: int = 0
    activeRecipientRequests: int = 0
    pendingDonorVerifications: int = 0
    pendingRecipientApprovals: int = 0
    recentApprovals: int = 0
    activeTransplantRequests: int = 0
    totalUsers: int = 0
    totalDonors: int = 0
    totalRecipients: int = 0
    totalHospitals: int = 0
    flaggedAccounts: int = 0


class AdminUserSummary(BaseModel):
    userId: str
    fullName: str
    email: str
    role: str
    profileStatus: str | None = None
    bloodGroup: str | None = None
    organs: list[str] = []
    organNeeded: str | None = None
    createdAt: str | None = None


class AdminUserListResponse(BaseModel):
    donors: list[AdminUserSummary] = []
    recipients: list[AdminUserSummary] = []
