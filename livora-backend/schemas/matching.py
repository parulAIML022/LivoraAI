from pydantic import BaseModel, Field


class MatchSuggestion(BaseModel):
    id: str
    counterpartUserId: str
    displayName: str
    initials: str
    bloodGroup: str | None = None
    compatibility: int
    location: str
    distance: str
    distanceKm: float
    urgency: str
    organType: str | None = None
    verificationStatus: str
    role: str = Field(description="donor or recipient — the matched party's role")


class MatchStats(BaseModel):
    totalMatches: int = 0
    nearbyMatches: int = 0
    averageCompatibility: int = 0
    newMatchesThisWeek: int = 0
    pendingRequests: int = 0
    verifiedDonors: int = 0
    activeRecipientRequests: int = 0


class UrgentAlert(BaseModel):
    message: str
    location: str | None = None
    matchId: str | None = None


class MatchingResponse(BaseModel):
    matches: list[MatchSuggestion] = []
    stats: MatchStats = Field(default_factory=MatchStats)
    urgentAlert: UrgentAlert | None = None
