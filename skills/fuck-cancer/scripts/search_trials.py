#!/usr/bin/env python3
"""Find cancer trials with an open site using ClinicalTrials.gov API v2.

This screens public trial records. It does not determine eligibility or
recommend treatment. Do not put patient identifiers in search arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


API_ROOT = "https://clinicaltrials.gov/api/v2"
OPEN_STATUSES = (
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ENROLLING_BY_INVITATION",
)
COUNTRY_ALIASES = {
    "ca": "Canada",
    "can": "Canada",
    "canada": "Canada",
    "uk": "United Kingdom",
    "unitedkingdom": "United Kingdom",
    "us": "United States",
    "usa": "United States",
    "unitedstates": "United States",
    "unitedstatesofamerica": "United States",
}
US_REGION_ALIASES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}
CANADA_REGION_ALIASES = {
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "NT": "Northwest Territories",
    "NU": "Nunavut",
    "ON": "Ontario",
    "PE": "Prince Edward Island",
    "QC": "Quebec",
    "SK": "Saskatchewan",
    "YT": "Yukon",
}
QUERY_STOPWORDS = {
    "a",
    "and",
    "cancer",
    "carcinoma",
    "for",
    "in",
    "neoplasm",
    "of",
    "or",
    "study",
    "the",
    "trial",
    "tumor",
    "tumour",
    "with",
}
TREATMENT_INTERVENTION_TYPES = {
    "BIOLOGICAL",
    "COMBINATION_PRODUCT",
    "DEVICE",
    "DIETARY_SUPPLEMENT",
    "DRUG",
    "GENETIC",
    "PROCEDURE",
    "RADIATION",
}
SUPPORTIVE_MARKERS = (
    "behavioral",
    "e-health",
    "exercise",
    "fear of",
    "interview",
    "quality of life",
    "supportive care",
    "survey",
)
PHASE_PRIORITY = {
    "PHASE3": 5,
    "PHASE2": 3,
    "PHASE1": 1,
    "EARLY_PHASE1": 1,
}


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


def alias_key(value: object) -> str:
    return "".join(character for character in clean(value).casefold() if character.isalnum())


def normalize_country(value: object) -> str:
    cleaned = clean(value)
    return COUNTRY_ALIASES.get(alias_key(cleaned), cleaned)


def normalize_region(value: object, country: str) -> str:
    cleaned = clean(value)
    code = cleaned.upper().replace(".", "")
    if country == "United States":
        return US_REGION_ALIASES.get(code, cleaned)
    if country == "Canada":
        return CANADA_REGION_ALIASES.get(code, cleaned)
    return cleaned


def normalize_location_args(args: argparse.Namespace) -> dict[str, str]:
    requested = {
        "country": clean(args.country),
        "state": clean(args.state),
        "city": clean(args.city),
    }
    args.country = normalize_country(args.country)
    args.state = normalize_region(args.state, args.country)
    args.city = clean(args.city)
    return requested


def query_tokens(value: object) -> set[str]:
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


def rank_results(results: list[dict], args: argparse.Namespace) -> list[dict]:
    return sorted(
        results,
        key=lambda item: (
            -relevance_score(item, args),
            item.get("overall_status") != "RECRUITING",
            -phase_priority(item),
            -date_ordinal(item.get("last_updated")),
            clean(item.get("title")).casefold(),
        ),
    )


def get_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "fuck-cancer-skill/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def site_matches(location: dict, args: argparse.Namespace) -> bool:
    if clean(location.get("status")).upper() not in OPEN_STATUSES:
        return False
    for field in ("country", "state", "city"):
        wanted = clean(getattr(args, field))
        actual = clean(location.get(field))
        if wanted and actual.casefold() != wanted.casefold():
            return False
    return True


def fetch_studies(args: argparse.Namespace) -> list[dict]:
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
        ]
    )
    params = {
        "query.cond": args.condition,
        "query.locn": args.country,
        "filter.overallStatus": "|".join(OPEN_STATUSES),
        "format": "json",
        "pageSize": "100",
        "fields": fields,
    }
    if args.terms:
        params["query.term"] = args.terms

    studies: list[dict] = []
    while True:
        url = f"{API_ROOT}/studies?{urllib.parse.urlencode(params)}"
        payload = get_json(url)
        studies.extend(payload.get("studies", []))
        token = payload.get("nextPageToken")
        if not token:
            return studies
        params["pageToken"] = token


def extract(study: dict, args: argparse.Namespace) -> dict | None:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    interventions = protocol.get("armsInterventionsModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    contacts = protocol.get("contactsLocationsModule", {})

    matching_sites = [
        location
        for location in contacts.get("locations", [])
        if site_matches(location, args)
    ]
    if not matching_sites:
        return None

    nct_id = clean(identification.get("nctId"))
    return {
        "nct_id": nct_id,
        "url": f"https://clinicaltrials.gov/study/{nct_id}",
        "title": clean(identification.get("briefTitle")),
        "overall_status": clean(status.get("overallStatus")),
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
        "eligibility_criteria": eligibility.get("eligibilityCriteria", ""),
        "open_sites": [
            {
                key: clean(site.get(key))
                for key in ("facility", "status", "city", "state", "country")
            }
            for site in matching_sites
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", required=True, help="Cancer type or condition")
    parser.add_argument("--terms", default="", help="Stage, biomarker, or treatment terms")
    parser.add_argument("--country", required=True)
    parser.add_argument("--state", default="", help="State, province, or region")
    parser.add_argument("--city", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path, help="Write JSON to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.limit < 1:
        print("--limit must be at least 1", file=sys.stderr)
        return 2

    requested_location = normalize_location_args(args)

    try:
        studies = fetch_studies(args)
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
            "normalized_from": requested_location
            if requested_location
            != {"country": args.country, "state": args.state, "city": args.city}
            else None,
            "open_site_statuses": list(OPEN_STATUSES),
        },
        "ranking": (
            "Condition and --terms matches, treatment focus, phase, "
            "recruitment status, and record recency."
        ),
        "result_count_before_limit": len(results),
        "results": results[: args.limit],
        "warning": (
            "These are screening candidates, not eligibility determinations or "
            "treatment recommendations. Confirm current availability and eligibility "
            "with the treating oncologist and trial site."
        ),
    }
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
