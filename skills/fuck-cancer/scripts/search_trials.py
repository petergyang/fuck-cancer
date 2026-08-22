#!/usr/bin/env python3
"""Find cancer trials with an open site using ClinicalTrials.gov API v2.

This screens public trial records. It does not determine eligibility or
recommend treatment. Do not put patient identifiers in search arguments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
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


def clean(value: object) -> str:
    return " ".join(str(value or "").split())


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

    try:
        studies = fetch_studies(args)
        results = [result for study in studies if (result := extract(study, args))]
        results.sort(
            key=lambda item: (
                item["overall_status"] != "RECRUITING",
                item["title"].casefold(),
            )
        )
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
            "open_site_statuses": list(OPEN_STATUSES),
        },
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
