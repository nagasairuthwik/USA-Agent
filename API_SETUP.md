# API Setup & Configuration Guide

This guide details all API providers used in the Agentic AI Travel Intelligence Platform (`USAAgent`), their authentication mechanisms, rate limits, coverage, and environment variable configuration.

---

## 1. Environment Variable Summary

All environment variables are loaded via `python-dotenv` from a local `.env` file (which is excluded from Git via `.gitignore`). Refer to `.env.example` for starter values.

| Variable Name | Required? | Default / Fallback | Provider Description |
| :--- | :--- | :--- | :--- |
| `GROQ_API_KEY` | Optional | Deterministic rail corridors fallback | Groq Cloud LLM for candidate suburban hub discovery |
| `GROQ_MODEL` | Optional | `llama-3.3-70b-versatile` | Model family for structured JSON candidate generation |
| `HERE_API_KEY` | Optional | Returns `NOT_CONFIGURED` status | HERE Maps Public Transit API v8 for door-to-door transit itineraries |
| `AMADEUS_CLIENT_ID` | Optional | Tavily web extraction fallback | Amadeus Self-Service Hotel Discovery OAuth2 |
| `AMADEUS_CLIENT_SECRET` | Optional | Tavily web extraction fallback | Amadeus Self-Service Hotel Discovery OAuth2 Secret |
| `TAVILY_API_KEY` | Recommended | Returns `NOT_CONFIGURED` / `UNAVAILABLE` | Tavily AI Search for live lodging extraction & safety evidence |

---

## 2. API Providers and Official Endpoints

### 1. OpenStreetMap Nominatim (Geocoding & CBD Anchor Resolution)
- **Official Documentation**: [https://nominatim.org/release-docs/latest/api/Search/](https://nominatim.org/release-docs/latest/api/Search/)
- **Usage Policy**: [https://operations.osmfoundation.org/policies/nominatim/](https://operations.osmfoundation.org/policies/nominatim/)
- **Authentication**: None required.
- **Header**: Requires a custom `User-Agent` (configured as `USAAgentTravelIntelligence/2.0`).
- **Rate Limit**: Maximum 1 request per second. Automatically enforced via internal sleep rate-limiter in `GeocodingTool`.
- **In-Memory Cache**: Active to minimize repeated lookups.

### 2. Groq Cloud API (Candidate Commuter Hub Discovery)
- **Official Documentation**: [https://console.groq.com/docs/quickstart](https://console.groq.com/docs/quickstart)
- **Key Registration**: [https://console.groq.com/keys](https://console.groq.com/keys)
- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Output Schema Enforcement**: Enforces `response_format: {"type": "json_object"}`.
- **Fallback**: If unconfigured or unavailable, automatically uses deterministic corridors.

### 3. HERE Maps Public Transit API v8 (Transit Routing & Stations)
- **Official Documentation**: [https://developer.here.com/documentation/public-transit-api/dev_guide/index.html](https://developer.here.com/documentation/public-transit-api/dev_guide/index.html)
- **Endpoint**: `https://transit.router.hereapi.com/v8/routes`
- **Authentication**: Query parameter `apiKey=YOUR_HERE_API_KEY`.
- **Handling when Unkeyed**: Explicitly labels results with `VerificationStatus.NOT_CONFIGURED` and provides provider provenance. Zero fake itineraries or schedules.

### 4. Amadeus Self-Service API (Hotel Shopping & Availability)
- **Official Documentation**: [https://developers.amadeus.com/self-service/category/hotel](https://developers.amadeus.com/self-service/category/hotel)
- **OAuth2 Token Endpoint**: `https://test.api.amadeus.com/v1/security/oauth2/token`
- **Hotel Offers Endpoint**: `https://test.api.amadeus.com/v3/shopping/hotel-offers`
- **Handling when Unkeyed**: Gracefully delegates to Tavily AI Search without breaking the pipeline.

### 5. Tavily AI Search (Real-Time Lodging Extraction & Attributable Safety)
- **Official Documentation**: [https://docs.tavily.com/](https://docs.tavily.com/)
- **Key Registration**: [https://app.tavily.com/](https://app.tavily.com/)
- **Endpoint**: `https://api.tavily.com/search`
- **Purpose**: Real-time extraction of live accommodation rates and neighborhood crime evidence.

---

## 3. Verification & Testing

Verify that all dependencies and tool endpoints are healthy:
```bash
py -m pytest -v
```
To launch the interactive dashboard:
```bash
py app.py
```
Open [http://localhost:8088](http://localhost:8088) in your web browser.
