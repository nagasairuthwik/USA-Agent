# Data Provenance & Verification Protocol

## 1. Principles of Provenance

The USAAgent platform enforces a zero-fabrication standard. Every data point across the pipeline carries explicit attribution, timestamping, source classification, and verification status.

```
+-----------------------------------------------------------------------------------+
|                              DATA PROVENANCE HIERARCHY                            |
+-----------------------------------------------------------------------------------+
| 1. API_VERIFIED    | Directly retrieved from official provider with structured ID  |
| 2. SEARCH_DERIVED  | Extracted with attributable snippet and direct source URL    |
| 3. ESTIMATED       | Calculated via documented physics / spatial bounds           |
| 4. NOT_CONFIGURED  | Provider key absent; explicit placeholder with provenance     |
| 5. UNAVAILABLE     | Query returned no verified matches; transparently null/empty  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Verification Status Matrix by Domain

### 1. Geographic Anchors & CBDs (`City_Master`)
- **Source**: OpenStreetMap Nominatim API / Official Metropolitan Transit Authority profile.
- **Fields**: `City_ID`, `City`, `State`, `Downtown_District`, `Primary_Transit_System`, `Latitude`, `Longitude`, `Last_Updated`, `Google_Maps_District_URL`.
- **Status Assigned**: `VERIFIED` (when coordinates match Nominatim reverse geocode) or `ESTIMATED` (when network fails and fallback is applied).

### 2. Public Transit Itineraries (`Transit_Connectivity`)
- **Source**: HERE Maps Public Transit API v8.
- **Fields**: `City`, `Downtown`, `Suburb`, `Transit_System`, `Transit_Mode`, `Nearest_Station`, `Commute_Minutes`, `Transfers`, `Fare_USD`.
- **Integrity Guarantee**: Commute times are never calculated using synthetic linear approximations (e.g. `4 + dist * 1.9` is eliminated). If HERE API credentials are absent, status is flagged as `NOT_CONFIGURED` with provider reference `Transit Routing (HERE API Not Configured)`.

### 3. Accommodations & Nightly Rates (`Accommodation_Master`)
- **Sources**: Amadeus Self-Service Hotel Offers API + Tavily AI Search (Booking.com Demand, Expedia Rapid, Google Hotels, Wyndham, Motel 6).
- **Fields**: `Base_Nightly_Rate_USD`, `Taxes_And_Fees_USD`, `Total_Booking_USD`, `Availability_Status`, `Check_In_Date`, `Check_Out_Date`, `Source_URL`, `Price_Source`, `Retrieval_Timestamp`, direct comparison links.
- **Budget Filter**: Strict deterministic mathematical filter `budget_min <= Base_Nightly_Rate_USD <= budget_max`. Out-of-bounds rates are rejected.

### 4. Neighborhood Safety Evidence (`Safety_Index`)
- **Source**: Attributable neighborhood crime reporting extracted via Tavily AI Search.
- **Evidence Storage**: Preserves `SafetyEvidence` records containing source title, URL, quote snippet, reporting period, and retrieval timestamp.
- **Handling Missing Data**: When evidence cannot be retrieved, `safety_score` and `crime_index` are recorded as `None` / `null` rather than a synthetic default.

### 5. Multi-Criteria Recommendation Scoring (`Recommendation_Score`)
- **Formula**: Deterministic MCDA:
  $$\text{Overall Score} = (w_{\text{safety}} \cdot S) + (w_{\text{cost}} \cdot C) + (w_{\text{commute}} \cdot M) + (w_{\text{transit}} \cdot T)$$
  where $\sum w_i = 1.0$.
- **Missing Safety Rule**: If safety evidence is absent, the weight of safety is proportionally distributed across cost, commute, and transit to ensure fair ranking.

### 6. Executive Report (`Final_Output`)
- Synthesizes all audited dimensions into actionable corporate travel itineraries with dynamic badge ranking (`#1 Recommended Location`, `Prime Alternative`, `Strong Value Option`).
