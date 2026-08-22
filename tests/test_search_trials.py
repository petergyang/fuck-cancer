"""Offline unit tests for the trial-search helper. No network required."""

import argparse
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "fuck-cancer"
    / "scripts"
    / "search_trials.py"
)
spec = importlib.util.spec_from_file_location("search_trials", SCRIPT)
search_trials = importlib.util.module_from_spec(spec)
sys.modules["search_trials"] = search_trials
spec.loader.exec_module(search_trials)


def make_args(**overrides):
    defaults = {
        "condition": "breast cancer",
        "terms": "",
        "country": "United States",
        "state": "",
        "city": "",
        "limit": 10,
        "full_criteria": False,
        "output": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def make_study(nct_id="NCT00000001", overall_status="RECRUITING", locations=None):
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "briefTitle": "A study",
            },
            "statusModule": {
                "overallStatus": overall_status,
                "lastUpdatePostDateStruct": {"date": "2026-01-01"},
            },
            "designModule": {"phases": ["PHASE3"], "studyType": "INTERVENTIONAL"},
            "armsInterventionsModule": {
                "interventions": [{"name": "Pembrolizumab"}],
            },
            "eligibilityModule": {
                "minimumAge": "18 Years",
                "maximumAge": "",
                "sex": "ALL",
                "eligibilityCriteria": "Inclusion: adults.",
            },
            "contactsLocationsModule": {
                "locations": locations
                or [
                    {
                        "facility": "General Hospital",
                        "status": "RECRUITING",
                        "city": "Los Angeles",
                        "state": "California",
                        "country": "United States",
                    }
                ],
            },
        }
    }


class NormalizationTests(unittest.TestCase):
    def test_country_aliases_expand(self):
        self.assertEqual(search_trials.normalize_country("USA"), "United States")
        self.assertEqual(search_trials.normalize_country("u.s."), "United States")
        self.assertEqual(search_trials.normalize_country("UK"), "United Kingdom")

    def test_unknown_country_passes_through(self):
        self.assertEqual(search_trials.normalize_country("France"), "France")

    def test_state_aliases_expand(self):
        self.assertEqual(search_trials.normalize_state("CA"), "California")
        self.assertEqual(search_trials.normalize_state("on"), "Ontario")

    def test_parse_args_normalizes_location(self):
        args = search_trials.parse_args(
            ["--condition", "breast cancer", "--country", "usa", "--state", "ca"]
        )
        self.assertEqual(args.country, "United States")
        self.assertEqual(args.state, "California")


class SiteMatchesTests(unittest.TestCase):
    def test_open_site_matches(self):
        location = {"status": "RECRUITING", "country": "United States"}
        self.assertTrue(
            search_trials.site_matches(location, make_args(), "RECRUITING")
        )

    def test_closed_site_rejected(self):
        location = {"status": "COMPLETED", "country": "United States"}
        self.assertFalse(
            search_trials.site_matches(location, make_args(), "RECRUITING")
        )

    def test_missing_site_status_falls_back_to_study_status(self):
        location = {"country": "United States"}
        self.assertTrue(
            search_trials.site_matches(location, make_args(), "RECRUITING")
        )
        self.assertFalse(
            search_trials.site_matches(location, make_args(), "COMPLETED")
        )

    def test_location_filters_are_case_insensitive(self):
        location = {
            "status": "RECRUITING",
            "city": "los angeles",
            "state": "california",
            "country": "united states",
        }
        args = make_args(state="California", city="Los Angeles")
        self.assertTrue(search_trials.site_matches(location, args, "RECRUITING"))

    def test_wrong_state_rejected(self):
        location = {
            "status": "RECRUITING",
            "state": "Texas",
            "country": "United States",
        }
        args = make_args(state="California")
        self.assertFalse(search_trials.site_matches(location, args, "RECRUITING"))


class ExtractTests(unittest.TestCase):
    def test_extracts_matching_study(self):
        result = search_trials.extract(make_study(), make_args())
        self.assertIsNotNone(result)
        self.assertEqual(result["nct_id"], "NCT00000001")
        self.assertEqual(result["open_sites"][0]["status"], "RECRUITING")

    def test_returns_none_without_matching_site(self):
        study = make_study(
            locations=[
                {
                    "facility": "Foreign Site",
                    "status": "RECRUITING",
                    "city": "Paris",
                    "state": "",
                    "country": "France",
                }
            ]
        )
        self.assertIsNone(search_trials.extract(study, make_args()))

    def test_missing_site_status_is_labeled_not_dropped(self):
        study = make_study(
            locations=[
                {
                    "facility": "General Hospital",
                    "city": "Los Angeles",
                    "state": "California",
                    "country": "United States",
                }
            ]
        )
        result = search_trials.extract(study, make_args())
        self.assertIsNotNone(result)
        self.assertEqual(
            result["open_sites"][0]["status"], "not listed (study is RECRUITING)"
        )

    def test_long_criteria_truncated_by_default(self):
        study = make_study()
        study["protocolSection"]["eligibilityModule"]["eligibilityCriteria"] = (
            "x" * 5000
        )
        result = search_trials.extract(study, make_args())
        self.assertIn("[Truncated", result["eligibility_criteria"])
        self.assertLess(len(result["eligibility_criteria"]), 2200)

    def test_full_criteria_flag_keeps_everything(self):
        study = make_study()
        study["protocolSection"]["eligibilityModule"]["eligibilityCriteria"] = (
            "x" * 5000
        )
        result = search_trials.extract(study, make_args(full_criteria=True))
        self.assertEqual(len(result["eligibility_criteria"]), 5000)


class SortingTests(unittest.TestCase):
    def test_recruiting_first_and_relevance_order_preserved(self):
        results = [
            {"overall_status": "NOT_YET_RECRUITING", "title": "A"},
            {"overall_status": "RECRUITING", "title": "Zebra"},
            {"overall_status": "RECRUITING", "title": "Apple"},
        ]
        results.sort(key=lambda item: item["overall_status"] != "RECRUITING")
        self.assertEqual(
            [item["title"] for item in results], ["Zebra", "Apple", "A"]
        )


if __name__ == "__main__":
    unittest.main()
