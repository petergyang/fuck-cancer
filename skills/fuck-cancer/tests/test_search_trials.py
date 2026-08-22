import argparse
import importlib.util
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "search_trials.py"
SPEC = importlib.util.spec_from_file_location("search_trials", SCRIPT_PATH)
search_trials = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(search_trials)


def make_args(**overrides):
    values = {
        "condition": "triple-negative breast cancer",
        "terms": "",
        "country": "USA",
        "state": "CA",
        "city": "",
        "limit": 3,
        "output": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


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


class LocationNormalizationTests(unittest.TestCase):
    def test_normalizes_us_country_and_state_abbreviations(self):
        args = make_args(country="USA", state="CA")

        requested = search_trials.normalize_location_args(args)

        self.assertEqual(requested["country"], "USA")
        self.assertEqual(args.country, "United States")
        self.assertEqual(args.state, "California")

    def test_normalizes_canadian_country_and_province_abbreviations(self):
        args = make_args(country="CAN", state="BC")

        search_trials.normalize_location_args(args)

        self.assertEqual(args.country, "Canada")
        self.assertEqual(args.state, "British Columbia")

    def test_matches_normalized_open_site(self):
        args = make_args(country="USA", state="CA")
        search_trials.normalize_location_args(args)
        location = {
            "status": "RECRUITING",
            "country": "United States",
            "state": "California",
            "city": "Burbank",
        }

        self.assertTrue(search_trials.site_matches(location, args))


class RankingTests(unittest.TestCase):
    def test_prioritizes_disease_specific_treatment_trial(self):
        args = make_args(country="United States", state="California")
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
        args = make_args(terms="previously untreated stage II")
        generic = make_result(
            "A Phase 3 Study in Breast Cancer",
            ["PHASE3"],
            ["DRUG"],
        )
        matching = make_result(
            "A Phase 2 Study in Breast Cancer",
            ["PHASE2"],
            ["DRUG"],
            "Includes previously untreated people with stage II disease.",
        )

        ranked = search_trials.rank_results([generic, matching], args)

        self.assertIs(ranked[0], matching)


class FetchTests(unittest.TestCase):
    def test_uses_normalized_country_and_paginates(self):
        args = make_args()
        search_trials.normalize_location_args(args)
        responses = [
            {"studies": [{"id": 1}], "nextPageToken": "next"},
            {"studies": [{"id": 2}]},
        ]

        with mock.patch.object(search_trials, "get_json", side_effect=responses) as get_json:
            studies = search_trials.fetch_studies(args)

        self.assertEqual(studies, [{"id": 1}, {"id": 2}])
        first_url = get_json.call_args_list[0].args[0]
        second_url = get_json.call_args_list[1].args[0]
        self.assertIn("query.locn=United+States", first_url)
        self.assertIn("pageToken=next", second_url)


if __name__ == "__main__":
    unittest.main()
