from pydantic import BaseModel, Field


class DonorMatchItem(BaseModel):
    donorName: str
    bloodGroup: str | None = None
    organ: str | None = None
    location: str | None = None
    status: str
    compatibilityScore: int = 95


class MatchStats(BaseModel):
    totalMatches: int = 0
    nearbyMatches: int = 0
    averageCompatibility: int = 0
    newMatchesThisWeek: int = 0
    pendingRequests: int = 0
    verifiedDonors: int = 0
    activeRecipientRequests: int = 0


class MatchingResponse(BaseModel):
    matches: list[DonorMatchItem] = []
    message: str | None = None
    stats: MatchStats = Field(default_factory=MatchStats)
