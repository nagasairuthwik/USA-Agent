"""
Typed Domain Models for Agentic Travel Intelligence Platform
Tracks typed entities, provenance, verification statuses, and report fields.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import datetime

class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    SEARCH_DERIVED = "SEARCH_DERIVED"
    UNVERIFIED = "UNVERIFIED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass
class Provenance:
    provider: str
    source_url: str = ""
    retrieval_timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    raw_reference: str = ""
    evidence_text: str = ""

@dataclass
class CityMaster:
    city_id: str
    city: str
    state: str
    downtown_district: str
    primary_transit_system: str
    latitude: float
    longitude: float
    last_updated: str
    google_maps_district_url: str = ""
    country: str = "US"
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    provenance: Optional[Provenance] = None

@dataclass
class TransitConnectivity:
    city: str
    downtown: str
    suburb: str
    transit_system: str
    transit_mode: str
    nearest_station: str
    commute_minutes: int
    transfers: int
    fare_usd: float
    google_maps_station_url: str = ""
    origin_coords: Optional[str] = None
    destination_coords: Optional[str] = None
    walking_time_minutes: int = 0
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    provider: str = "Transit Routing API"
    retrieval_timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

@dataclass
class Accommodation:
    city: str
    locality: str
    hotel_name: str
    address: str
    currency: str = "USD"
    base_nightly_rate_usd: float = 0.0
    taxes_and_fees_usd: float = 0.0
    total_booking_usd: float = 0.0
    availability_status: str = "Available"
    check_in_date: str = ""
    check_out_date: str = ""
    occupancy: str = "1 Room, 2 Adults"
    source_url: str = ""
    price_source: str = "Live API Offer"
    retrieval_timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    google_hotels_url: str = ""
    google_maps_url: str = ""
    booking_demand_api_url: str = ""
    expedia_rapid_api_url: str = ""
    wyndham_official_url: str = ""
    tavily_verified: bool = True
    rating: float = 4.0
    review_count: int = 100
    distance_to_station_miles: float = 0.3
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    # Backward compatibility property for nightly_rate_usd
    @property
    def nightly_rate_usd(self) -> float:
        return self.base_nightly_rate_usd
    @nightly_rate_usd.setter
    def nightly_rate_usd(self, value: float):
        self.base_nightly_rate_usd = value

@dataclass
class SafetyEvidence:
    claim: str
    source_title: str
    source_url: str
    retrieval_timestamp: str
    metric_type: str = "Crime Sentiment / Index"
    reporting_period: str = "Recent"
    geographic_scope: str = "Neighborhood"
    is_official_statistics: bool = False

@dataclass
class SafetyIndex:
    city: str
    locality: str
    safety_score: Optional[float]
    crime_index: Optional[float]
    walkability: int
    category: str
    evidence_coverage: float = 1.0
    evidence_list: List[SafetyEvidence] = field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED

@dataclass
class RecommendationScore:
    city: str
    locality: str
    safety_score: Optional[float]
    cost_score: float
    commute_score: float
    transit_score: float
    overall_score: float
    rank: int
    is_rankable: bool = True
    scoring_notes: str = ""

@dataclass
class FinalOutput:
    city: str
    downtown: str
    recommended_locality: str
    transit_system: str
    station: str
    commute_time: str
    hotel: str
    rate: float                      # Verified base rate
    taxes_and_fees: float
    total_booking: float
    currency: str
    availability_status: str
    source_url: str
    price_source: str
    retrieval_timestamp: str
    google_hotels_url: str
    google_maps_url: str
    booking_demand_api_url: str
    expedia_rapid_api_url: str
    wyndham_official_url: str
    safety: float
    overall_score: float
    recommendation: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    rejection_reasons: List[str] = field(default_factory=list)
