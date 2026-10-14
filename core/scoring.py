"""
Deterministic Multi-Criteria Decision Analysis (MCDA) Scoring Engine
Multi-factor weights: 35% Safety, 30% Cost, 20% Commute, 15% Transit
"""

from typing import List, Dict, Optional, Tuple
from core.models import (
    TransitConnectivity,
    Accommodation,
    SafetyIndex,
    RecommendationScore
)

class DeterministicScorer:
    """
    Deterministic scoring engine implementing transparent multi-criteria decision analysis.
    Enforces that weights sum to 1.0 within tolerance.
    Handles missing values and boundaries deterministically.
    """

    def __init__(
        self,
        weight_safety: float = 0.35,
        weight_cost: float = 0.30,
        weight_commute: float = 0.20,
        weight_transit: float = 0.15,
        budget_min: float = 50.0,
        budget_max: float = 60.0,
        max_commute_minutes: int = 90
    ):
        self.weight_safety = float(weight_safety)
        self.weight_cost = float(weight_cost)
        self.weight_commute = float(weight_commute)
        self.weight_transit = float(weight_transit)
        self.budget_min = float(budget_min)
        self.budget_max = float(budget_max)
        self.max_commute_minutes = int(max_commute_minutes)

        total_weights = self.weight_safety + self.weight_cost + self.weight_commute + self.weight_transit
        if abs(total_weights - 1.0) > 0.001:
            raise ValueError(f"Scoring weights must sum to 1.0, got {total_weights:.4f}")

    def score_candidate(
        self,
        accomm: Accommodation,
        transit: TransitConnectivity,
        safety: SafetyIndex
    ) -> RecommendationScore:
        """
        Calculates normalized scores for a single validated candidate.
        """
        # 1. Cost Score (Lower rate within budget bracket = higher score)
        rate = accomm.base_nightly_rate_usd
        budget_span = max(1.0, self.budget_max - self.budget_min)
        rel_pos = max(0.0, min(1.0, (rate - self.budget_min) / budget_span))
        base_cost = 98.0 - (rel_pos * 14.0)
        rating_bonus = (accomm.rating - 3.5) * 6.0
        cost_score = min(100.0, max(30.0, round(base_cost + rating_bonus, 1)))

        # 2. Commute Score (Shorter travel duration = higher score)
        commute_m = transit.commute_minutes
        commute_ratio = min(1.0, max(0.0, commute_m / float(self.max_commute_minutes)))
        commute_score = round(100.0 - (commute_ratio * 40.0), 1)

        # 3. Transit Score (Direct rail / fewer transfers = higher score)
        transfer_penalty = transit.transfers * 12.0
        fare_penalty = max(0.0, (transit.fare_usd - 2.50) * 1.5)
        transit_score = round(max(50.0, min(100.0, 95.0 - transfer_penalty - fare_penalty)), 1)

        # 4. Safety Score handling
        is_rankable = True
        notes = []
        if safety.safety_score is None:
            # Missing safety evidence cannot be fabricated; candidate flagged
            safety_score = None
            effective_safety = 50.0  # fallback baseline for computation
            is_rankable = False
            notes.append("Safety data UNKNOWN; excluded from verified top ranking")
        else:
            safety_score = float(safety.safety_score)
            effective_safety = safety_score

        # Composite MCDA Score calculation
        overall_score = round(
            (effective_safety * self.weight_safety) +
            (cost_score * self.weight_cost) +
            (commute_score * self.weight_commute) +
            (transit_score * self.weight_transit),
            2
        )

        return RecommendationScore(
            city=accomm.city,
            locality=accomm.locality,
            safety_score=safety_score,
            cost_score=cost_score,
            commute_score=commute_score,
            transit_score=transit_score,
            overall_score=overall_score,
            rank=0,  # Assigned in batch ranking
            is_rankable=is_rankable,
            scoring_notes="; ".join(notes)
        )

    def score_candidates(
        self,
        transits: List[TransitConnectivity],
        accomms: List[Accommodation],
        safeties: List[SafetyIndex],
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None
    ) -> List[RecommendationScore]:
        """
        Batch scores and ranks all accommodations matching transits and safeties.
        """
        if budget_min is not None:
            self.budget_min = float(budget_min)
        if budget_max is not None:
            self.budget_max = float(budget_max)

        transit_map = {(t.city, t.suburb): t for t in transits}
        safety_map = {(s.city, s.locality): s for s in safeties}

        pairs = []
        for a in accomms:
            t = transit_map.get((a.city, a.locality))
            s = safety_map.get((a.city, a.locality))
            if t and s:
                pairs.append((a, t, s))

        return self.rank_candidates(pairs)

    def rank_candidates(
        self,
        candidates: List[Tuple[Accommodation, TransitConnectivity, SafetyIndex]]
    ) -> List[RecommendationScore]:
        """
        Scores and ranks all candidates deterministically by overall_score descending.
        """
        scores = []
        for accomm, transit, safety in candidates:
            score = self.score_candidate(accomm, transit, safety)
            scores.append(score)

        # Sort: rankable candidates first, then by overall_score descending
        scores.sort(key=lambda s: (s.is_rankable, s.overall_score), reverse=True)

        for idx, score in enumerate(scores, start=1):
            score.rank = idx

        return scores
