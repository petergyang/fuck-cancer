"""Offline unit tests for the trial-search helper. No network required."""

import argparse
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

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
        "near": None,
        "radius_miles": 50.0,
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
                "interventions": [{"name": "Pembrolizumab", "type": "DRUG"}],
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


def make_result(title, phases, intervention_types, eligibility=""):
    return {
        "title": title,
        "overall_status": "RECRUITING",
        "last_updated": "2026-08-01",
        "phases": phases,
        "study_type": "INTERVENTIONAL",
        "interventions": [],
        "intervention_types": intervention_types,
        "eligibility_criteria": eligibility,
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
    def test_prioritizes_disease_specific_treatment_trial(self):
        args = make_args(condition="triple-negative breast cancer")
        supportive = make_result(
            "An e-Health Intervention for Women With Breast Cancer",
            ["NA"],
            ["BEHAVIORAL"],
            "Includes stage II triple negative breast cancer.",
        )
        basket = make_result(
            "A Beta-only IL-2 Immunotherapy Study",
            ["PHASE1", "PHASE2"],
            ["DRUG", "BIOLOGICAL"],
            "Includes locally advanced or metastatic solid tumors.",
        )
        specific = make_result(
            "A Phase 3 Study in People With Breast Cancer",
            ["PHASE3"],
            ["DRUG"],
            "Includes previously untreated triple-negative breast cancer.",
        )

        ranked = search_trials.rank_results([supportive, basket, specific], args)

        self.assertIs(ranked[0], specific)
        self.assertIs(ranked[-1], supportive)

    def test_prioritizes_user_terms(self):
        args = make_args(
            condition="triple-negative breast cancer",
            terms="previously untreated stage II",
        )
        generic = make_result(
            "A Phase 3 Study in Breast Cancer", ["PHASE3"], ["DRUG"]
        )
        matching = make_result(
            "A Phase 2 Study in Breast Cancer",
            ["PHASE2"],
            ["DRUG"],
            "Includes previously untreated people with stage II disease.",
        )

        ranked = search_trials.rank_results([generic, matching], args)

        self.assertIs(ranked[0], matching)

    def test_api_order_breaks_exact_ties(self):
        args = make_args()
        first = make_result("Zebra", ["PHASE2"], ["DRUG"])
        second = make_result("Apple", ["PHASE2"], ["DRUG"])

        ranked = search_trials.rank_results([first, second], args)

        self.assertEqual([item["title"] for item in ranked], ["Zebra", "Apple"])


class FetchTests(unittest.TestCase):
    def test_uses_normalized_location_and_paginates(self):
        args = search_trials.parse_args(
            ["--condition", "breast cancer", "--country", "USA", "--state", "CA"]
        )
        responses = [
            {"studies": [{"id": 1}], "nextPageToken": "next"},
            {"studies": [{"id": 2}]},
        ]

        with mock.patch.object(search_trials, "get_json", side_effect=responses) as get_json:
            studies, truncated = search_trials.fetch_studies(args)

        self.assertEqual(studies, [{"id": 1}, {"id": 2}])
        self.assertFalse(truncated)
        first_url = get_json.call_args_list[0].args[0]
        second_url = get_json.call_args_list[1].args[0]
        self.assertIn("query.locn=California%2C+United+States", first_url)
        self.assertIn("pageToken=next", second_url)


LOS_ANGELES = (34.0522, -118.2437)


class GeoTests(unittest.TestCase):
    def test_parse_near_accepts_lat_lon(self):
        self.assertEqual(search_trials.parse_near("34.05, -118.24"), (34.05, -118.24))
        self.assertIsNone(search_trials.parse_near(""))

    def test_parse_near_rejects_bad_input(self):
        for value in ("Los Angeles", "34.05", "95,0", "a,b"):
            with self.assertRaises(argparse.ArgumentTypeError):
                search_trials.parse_near(value)

    def test_distance_is_roughly_correct(self):
        # Los Angeles to San Diego is about 112 miles.
        miles = search_trials.distance_miles(LOS_ANGELES, {"lat": 32.7157, "lon": -117.1611})
        self.assertAlmostEqual(miles, 112, delta=5)
        self.assertIsNone(search_trials.distance_miles(LOS_ANGELES, {}))

    def test_near_keeps_close_sites_and_drops_far_or_unlocated_ones(self):
        args = make_args(near=LOS_ANGELES, radius_miles=40)
        close = {"status": "RECRUITING", "country": "United States",
                 "city": "Torrance", "geoPoint": {"lat": 33.8358, "lon": -118.3406}}
        far = {"status": "RECRUITING", "country": "United States",
               "city": "San Diego", "geoPoint": {"lat": 32.7157, "lon": -117.1611}}
        unlocated = {"status": "RECRUITING", "country": "United States", "city": "Unknown"}
        self.assertTrue(search_trials.site_matches(close, args, "RECRUITING"))
        self.assertFalse(search_trials.site_matches(far, args, "RECRUITING"))
        self.assertFalse(search_trials.site_matches(unlocated, args, "RECRUITING"))

    def test_extract_reports_distance_and_sorts_nearest_first(self):
        args = make_args(near=LOS_ANGELES, radius_miles=60)
        study = make_study(locations=[
            {"facility": "Far", "status": "RECRUITING", "city": "Irvine",
             "country": "United States", "geoPoint": {"lat": 33.6695, "lon": -117.8231}},
            {"facility": "Near", "status": "RECRUITING", "city": "Beverly Hills",
             "country": "United States", "geoPoint": {"lat": 34.0736, "lon": -118.4004}},
        ])
        result = search_trials.extract(study, args)
        self.assertEqual([site["facility"] for site in result["open_sites"]], ["Near", "Far"])
        self.assertLess(result["open_sites"][0]["distance_miles"], 15)

    def test_fetch_sends_geo_filter(self):
        args = search_trials.parse_args([
            "--condition", "breast cancer", "--country", "USA",
            "--near", "34.05,-118.24", "--radius-miles", "40",
        ])
        with mock.patch.object(search_trials, "get_json", return_value={"studies": []}) as get_json:
            search_trials.fetch_studies(args)
        self.assertIn("filter.geo=distance%2834.05%2C-118.24%2C40.0mi%29", get_json.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
