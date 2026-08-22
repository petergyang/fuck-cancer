#!/usr/bin/env python3
"""Find cancer trials with an open site using ClinicalTrials.gov API v2.

This screens public trial records. It does not determine eligibility or
recommend treatment. Do not put patient identifiers in search arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple


API_ROOT = "https://clinicaltrials.gov/api/v2"
OPEN_STATUSES = (
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ENROLLING_BY_INVITATION",
)
STATUS_NOTES = {
    "NOT_YET_RECRUITING": (
        "This site is expected to open but cannot screen patients yet."
    ),
    "ENROLLING_BY_INVITATION": (
        "Enrollment is by invitation only; patients cannot volunteer directly."
    ),
}
PAGE_SIZE = 1000  # API v2 maximum
MAX_PAGES = 5
REQUEST_ATTEMPTS = 3
CRITERIA_PREVIEW_CHARS = 2000

# ClinicalTrials.gov stores full location names ("United States", "California").
# Expand the abbreviations people actually type so a search does not silently
# return zero results.
COUNTRY_ALIASES = {
    "us": "United States",
    "usa": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "america": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "uae": "United Arab Emirates",
    "south korea": "Korea, Republic of",
}
STATE_ALIASES = {
    "al": "Alabama", "ak": "Alaska", "az": "Arizona", "ar": "Arkansas",
    "ca": "California", "co": "Colorado", "ct": "Connecticut",
    "de": "Delaware", "fl": "Florida", "ga": "Georgia", "hi": "Hawaii",
    "id": "Idaho", "il": "Illinois", "in": "Indiana", "ia": "Iowa",
    "ks": "Kansas", "ky": "Kentucky", "la": "Louisiana", "me": "Maine",
    "md": "Maryland", "ma": "Massachusetts", "mi": "Michigan",
    "mn": "Minnesota", "ms": "Mississippi", "mo": "Missouri",
    "mt": "Montana", "ne": "Nebraska", "nv": "Nevada",
    "nh": "New Hampshire", "nj": "New Jersey", "nm": "New Mexico",
    "ny": "New York", "nc": "North Carolina", "nd": "North Dakota",
    "oh": "Ohio", "ok": "Oklahoma", "or": "Oregon", "pa": "Pennsylvania",
    "ri": "Rhode Island", "sc": "South Carolina", "sd": "South Dakota",
    "tn": "Tennessee", "tx": "Texas", "ut": "Utah", "vt": "Vermont",
    "va": "Virginia", "wa": "Washington", "wv": "West Virginia",
    "wi": "Wisconsin", "wy": "Wyoming", "dc": "District of Columbia",
    "pr": "Puerto Rico",
    "ab": "Alberta", "bc": "British Columbia", "mb": "Manitoba",
    "nb": "New Brunswick", "nl": "Newfoundland and Labrador",
    "ns": "Nova Scotia", "on": "Ontario", "pe": "Prince Edward Island",
    "qc": "Quebec", "sk": "Saskatchewan",
}
QUERY_STOPWORDS = {
    "a", "and", "cancer", "carcinoma", "for", "in", "neoplasm", "of",
    "or", "study", "the", "trial", "tumor", "tumour", "with",
}
TREATMENT_INTERVENTION_TYPES = {
    "BIOLOGICAL", "COMBINATION_PRODUCT", "DEVICE", "DIETARY_SUPPLEMENT",
    "DRUG", "GENETIC", "PROCEDURE", "RADIATION",
}
SUPPORTIVE_MARKERS = (
    "behavioral", "e-health", "exercise", "fear of", "interview",
    "quality of life", "supportive care", "survey",
)
DEFAULT_RADIUS_MILES = 50
EARTH_RADIUS_MILES = 3958.8
PHASE_PRIORITY = {
    "PHASE3": 5,
    "PHASE2": 3,
    "PHASE1": 1,
    "EARLY_PHASE1": 1,
}


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def normalize_country(value: str) -> str:
    cleaned = clean(value)
    return COUNTRY_ALIASES.get(cleaned.casefold(), cleaned)


def normalize_state(value: str) -> str:
    cleaned = clean(value)
    return STATE_ALIASES.get(cleaned.casefold(), cleaned)


def parse_near(value: str) -> Optional[Tuple[float, float]]:
    """Parse "LAT,LON" into floats. Returns None for an empty value."""
    cleaned = clean(value)
    if not cleaned:
        return None
    parts = [part.strip() for part in cleaned.split(",")]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("--near expects LAT,LON such as 34.05,-118.24")
    try:
        lat, lon = float(parts[0]), float(parts[1])
    except ValueError as error:
        raise argparse.ArgumentTypeError("--near expects numeric LAT,LON") from error
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise argparse.ArgumentTypeError("--near coordinates are out of range")
    return lat, lon


def distance_miles(origin: Tuple[float, float], point: dict) -> Optional[float]:
    """Great-circle distance from origin to a site's geoPoint, or None if missing."""
    try:
        lat2 = float(point["lat"])
        lon2 = float(point["lon"])
    except (KeyError, TypeError, ValueError):
        return None
    lat1, lon1 = map(math.radians, origin)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)
    a = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def query_tokens(value: object) -> set:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", clean(value).casefold())
        if len(token) > 1 and token not in QUERY_STOPWORDS
    }


def phase_priority(item: dict) -> int:
    return max(
        (PHASE_PRIORITY.get(clean(phase).upper(), 0) for phase in item.get("phases", [])),
        default=0,
    )


def relevance_score(item: dict, args: argparse.Namespace) -> int:
    title = clean(item.get("title")).casefold()
    interventions = " ".join(item.get("interventions", [])).casefold()
    eligibility = clean(item.get("eligibility_criteria")).casefold()
    condition_tokens = query_tokens(args.condition)
    term_tokens = query_tokens(args.terms)

    score = 0
    score += 3 * len(condition_tokens & query_tokens(title))
    score += 2 * len(condition_tokens & query_tokens(interventions))
    score += min(3, len(condition_tokens & query_tokens(eligibility)))
    score += 5 * len(term_tokens & query_tokens(title))
    score += 3 * len(term_tokens & query_tokens(interventions))
    score += 2 * len(term_tokens & query_tokens(eligibility))
    score += phase_priority(item)

    intervention_types = {
        clean(value).upper() for value in item.get("intervention_types", [])
    }
    if intervention_types & TREATMENT_INTERVENTION_TYPES:
        score += 4
    if item.get("overall_status") == "RECRUITING":
        score += 2
    if any(marker in f"{title} {interventions}" for marker in SUPPORTIVE_MARKERS):
        score -= 4
    return score


def date_ordinal(value: object) -> int:
    try:
        return dt.date.fromisoformat(clean(value)).toordinal()
    except ValueError:
        return 0


def rank_results(results: List[dict], args: argparse.Namespace) -> List[dict]:
    # Sorting is stable, so the API's relevance order breaks exact ties.
    return sorted(
        results,
        key=lambda item: (
            -relevance_score(item, args),
            item.get("overall_status") != "RECRUITING",
            -phase_priority(item),
            -date_ordinal(item.get("last_updated")),
        ),
    )


def get_json(url: str) -> dict:
    last_error: Exception = RuntimeError("request not attempted")
    for attempt in range(REQUEST_ATTEMPTS):
        if attempt:
            time.sleep(2 ** attempt)
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "fuck-cancer-skill/1.0"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            last_error = error
        except OSError as error:
            last_error = error
    raise last_error


def site_matches(location: dict, args: argparse.Namespace, overall_status: str) -> bool:
    site_status = clean(location.get("status")).upper()
    if site_status:
        if site_status not in OPEN_STATUSES:
            return False
    elif overall_status.upper() not in OPEN_STATUSES:
        # Many records omit per-site status; fall back to the study status
        # rather than silently dropping a recruiting study's sites.
        return False
    for field in ("country", "state", "city"):
        wanted = clean(getattr(args, field))
        actual = clean(location.get(field))
        if wanted and actual.casefold() != wanted.casefold():
            return False
    near = getattr(args, "near", None)
    if near:
        distance = distance_miles(near, location.get("geoPoint") or {})
        if distance is None or distance > args.radius_miles:
            return False
    return True


def fetch_studies(args: argparse.Namespace) -> Tuple[List[dict], bool]:
    fields = ",".join(
        [
            "NCTId",
            "BriefTitle",
            "OverallStatus",
            "LastUpdatePostDate",
            "Phase",
            "StudyType",
            "InterventionName",
            "InterventionType",
            "EligibilityCriteria",
            "Sex",
            "MinimumAge",
            "MaximumAge",
            "LocationFacility",
            "LocationStatus",
            "LocationCity",
            "LocationState",
            "LocationCountry",
            "LocationGeoPoint",
        ]
    )
    location_query = ", ".join(
        part for part in (args.city, args.state, args.country) if part
    )
    params = {
        "query.cond": args.condition,
        "query.locn": location_query,
        "filter.overallStatus": "|".join(OPEN_STATUSES),
        "format": "json",
        "pageSize": str(PAGE_SIZE),
        "fields": fields,
    }
    if args.terms:
        params["query.term"] = args.terms
    if getattr(args, "near", None):
        lat, lon = args.near
        params["filter.geo"] = f"distance({lat},{lon},{args.radius_miles}mi)"

    studies: list[dict] = []
    for _ in range(MAX_PAGES):
        url = f"{API_ROOT}/studies?{urllib.parse.urlencode(params)}"
        payload = get_json(url)
        studies.extend(payload.get("studies", []))
        token = payload.get("nextPageToken")
        if not token:
            return studies, False
        params["pageToken"] = token
    return studies, True


def preview_criteria(text: object, full: bool) -> str:
    criteria = str(text or "")
    if full or len(criteria) <= CRITERIA_PREVIEW_CHARS:
        return criteria
    return (
        criteria[:CRITERIA_PREVIEW_CHARS].rstrip()
        + "\n[Truncated. Read the full criteria at the study link or rerun "
        "with --full-criteria.]"
    )


def extract(study: dict, args: argparse.Namespace) -> Optional[dict]:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    interventions = protocol.get("armsInterventionsModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    contacts = protocol.get("contactsLocationsModule", {})

    overall_status = clean(status.get("overallStatus"))
    matching_sites = [
        location
        for location in contacts.get("locations", [])
        if site_matches(location, args, overall_status)
    ]
    if not matching_sites:
        return None

    nct_id = clean(identification.get("nctId"))
    near = getattr(args, "near", None)

    def site_entry(site: dict) -> dict:
        entry = {
            "facility": clean(site.get("facility")),
            "status": clean(site.get("status"))
            or f"not listed (study is {overall_status})",
            "city": clean(site.get("city")),
            "state": clean(site.get("state")),
            "country": clean(site.get("country")),
        }
        if near:
            distance = distance_miles(near, site.get("geoPoint") or {})
            entry["distance_miles"] = round(distance) if distance is not None else None
        return entry

    open_sites = [site_entry(site) for site in matching_sites]
    if near:
        open_sites.sort(key=lambda site: site["distance_miles"] or 0)
    return {
        "nct_id": nct_id,
        "url": f"https://clinicaltrials.gov/study/{nct_id}",
        "title": clean(identification.get("briefTitle")),
        "overall_status": overall_status,
        "last_updated": clean(status.get("lastUpdatePostDateStruct", {}).get("date")),
        "phases": design.get("phases", []),
        "study_type": clean(design.get("studyType")),
        "interventions": [
            clean(item.get("name"))
            for item in interventions.get("interventions", [])
            if clean(item.get("name"))
        ],
        "intervention_types": sorted(
            {
                clean(item.get("type"))
                for item in interventions.get("interventions", [])
                if clean(item.get("type"))
            }
        ),
        "age_and_sex": {
            "minimum_age": clean(eligibility.get("minimumAge")),
            "maximum_age": clean(eligibility.get("maximumAge")),
            "sex": clean(eligibility.get("sex")),
        },
        "eligibility_criteria": preview_criteria(
            eligibility.get("eligibilityCriteria", ""), args.full_criteria
        ),
        "open_sites": open_sites,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", required=True, help="Cancer type or condition")
    parser.add_argument("--terms", default="", help="Stage, biomarker, or treatment terms")
    parser.add_argument("--country", required=True)
    parser.add_argument("--state", default="", help="State, province, or region")
    parser.add_argument("--city", default="")
    parser.add_argument(
        "--near",
        type=parse_near,
        default=None,
        help="LAT,LON of the patient's home area, e.g. 34.05,-118.24 for Los Angeles",
    )
    parser.add_argument(
        "--radius-miles",
        type=float,
        default=DEFAULT_RADIUS_MILES,
        help=f"Keep only sites within this many miles of --near (default {DEFAULT_RADIUS_MILES})",
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--full-criteria",
        action="store_true",
        help="Include full eligibility criteria instead of a preview",
    )
    parser.add_argument("--output", type=Path, help="Write JSON to this path")
    args = parser.parse_args(argv)
    args.country = normalize_country(args.country)
    args.state = normalize_state(args.state)
    args.city = clean(args.city)
    return args


def main() -> int:
    args = parse_args()
    if args.limit < 1:
        print("--limit must be at least 1", file=sys.stderr)
        return 2
    if args.radius_miles <= 0:
        print("--radius-miles must be greater than 0", file=sys.stderr)
        return 2

    try:
        studies, truncated = fetch_studies(args)
        results = [result for study in studies if (result := extract(study, args))]
        results = rank_results(results, args)
        version = get_json(f"{API_ROOT}/version")
    except Exception as error:
        print(f"ClinicalTrials.gov request failed: {error}", file=sys.stderr)
        return 1

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "clinicaltrials_gov_data_timestamp": clean(version.get("dataTimestamp")),
        "search": {
            "condition": args.condition,
            "terms": args.terms,
            "country": args.country,
            "state": args.state,
            "city": args.city,
            "near": list(args.near) if args.near else None,
            "radius_miles": args.radius_miles if args.near else None,
            "open_site_statuses": list(OPEN_STATUSES),
            "status_notes": STATUS_NOTES,
        },
        "ranking": (
            "Condition and --terms matches, treatment focus, phase, "
            "recruitment status, record recency, and API relevance."
        ),
        "search_truncated": truncated,
        "result_count_before_limit": len(results),
        "results": results[: args.limit],
        "warning": (
            "These are screening candidates, not eligibility determinations or "
            "treatment recommendations. Confirm current availability and eligibility "
            "with the treating oncologist and trial site."
        ),
    }
    if truncated:
        payload["truncation_note"] = (
            "The search matched more studies than this tool retrieves. Narrow the "
            "condition, terms, or location to see everything relevant."
        )
    if not results:
        payload["hint"] = (
            "No open sites matched. Location matching is exact: use full names such "
            "as 'United States' or 'California' (common abbreviations like USA or CA "
            "are expanded automatically), check spelling, or widen the search by "
            "dropping --city or --state, or by using --near LAT,LON with a larger "
            "--radius-miles."
        )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {len(payload['results'])} candidate trials to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
