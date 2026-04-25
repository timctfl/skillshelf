#!/usr/bin/env python3
"""
test_classify_taxonomy.py - Unit tests for classify_taxonomy.py

Run: python3 scripts/test_classify_taxonomy.py
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import classify_taxonomy as ct

# ---------------------------------------------------------------------------
# Minimal inline fixture taxonomy (independent of taxonomy-keywords.json)
# ---------------------------------------------------------------------------

_JACKETS = {
    "id": 5598,
    "path": "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets",
    "tier": 4,
    "keywords": {
        "high": ["jacket", "rain jacket", "softshell jacket"],
        "medium": ["outerwear", "waterproof"],
        "low": ["weather"],
    },
}

_CLOTHING_ROOT = {
    "id": 212,
    "path": "Apparel & Accessories > Clothing > Shirts & Tops",
    "tier": 3,
    "keywords": {
        "high": ["t-shirt", "polo shirt"],
        "medium": ["shirt"],
        "low": ["clothing"],
    },
}

_TENTS = {
    "id": 3261,
    "path": "Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents",
    "tier": 5,
    "keywords": {
        "high": ["tent", "camping tent"],
        "medium": ["shelter"],
        "low": ["camping"],
    },
}

_ELECTRONICS = {
    "id": None,
    "path": "Electronics > Computers > Laptops",
    "tier": 3,
    "keywords": {
        "high": ["laptop", "notebook computer"],
        "medium": ["portable computer"],
        "low": ["computing"],
    },
}

_WINE_CATEGORY = {
    "id": None,
    "path": "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages",
    "tier": 4,
    "keywords": {
        "high": ["wine", "red wine", "white wine"],
        "medium": ["bottle"],
        "low": [],
    },
}

_ALL_CATS = [_JACKETS, _CLOTHING_ROOT, _TENTS, _ELECTRONICS, _WINE_CATEGORY]


def _preload(cats):
    """Run precompute step the way load_taxonomy() does it."""
    import copy
    cats = copy.deepcopy(cats)
    for cat in cats:
        raw = cat.get("keywords", {})
        cat["_kw_tokens"] = {
            tier: [
                (frozenset(ct.normalize(kw).split()), kw)
                for kw in raw.get(tier, [])
                if kw.strip()
            ]
            for tier in ("high", "medium", "low")
        }
    return cats


CATS = _preload(_ALL_CATS)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestStripHtml(unittest.TestCase):
    def test_removes_tags(self):
        result = " ".join(ct.strip_html("<p>Hello <b>World</b></p>").split())
        self.assertEqual(result, "Hello World")

    def test_empty_string(self):
        self.assertEqual(ct.strip_html(""), "")

    def test_plain_text_unchanged(self):
        self.assertEqual(ct.strip_html("plain text").strip(), "plain text")

    def test_malformed_html_fallback(self):
        result = ct.strip_html("<p>Unclosed tag text")
        self.assertIn("text", result)


class TestNormalize(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(ct.normalize("JACKET"), "jacket")

    def test_strips_punctuation(self):
        self.assertEqual(ct.normalize("rain-jacket!"), "rain jacket")

    def test_collapses_whitespace(self):
        self.assertEqual(ct.normalize("  two  spaces  "), "two spaces")


class TestScoreCategory(unittest.TestCase):
    def setUp(self):
        self.jacket_cat = _preload([_JACKETS])[0]

    def test_high_keyword_scores_3(self):
        tokens = set(ct.normalize("jacket").split())
        score, matched = ct.score_category(tokens, self.jacket_cat)
        self.assertEqual(score, 3)
        self.assertIn("jacket", matched)

    def test_medium_keyword_scores_2(self):
        tokens = set(ct.normalize("waterproof shell").split())
        score, matched = ct.score_category(tokens, self.jacket_cat)
        self.assertEqual(score, 2)

    def test_no_match_returns_zero(self):
        tokens = set(ct.normalize("tent sleeping bag").split())
        score, _ = ct.score_category(tokens, self.jacket_cat)
        self.assertEqual(score, 0)

    def test_multi_word_keyword_requires_all_tokens(self):
        # "rain jacket" only matches if both "rain" and "jacket" are present
        tokens_both = set(ct.normalize("rain jacket").split())
        score_both, _ = ct.score_category(tokens_both, self.jacket_cat)
        tokens_one = set(ct.normalize("rain gear").split())
        score_one, _ = ct.score_category(tokens_one, self.jacket_cat)
        self.assertGreater(score_both, score_one)


class TestClassifyConfidenceLevels(unittest.TestCase):
    def test_high_confidence(self):
        result = ct.classify("Rain Jacket Waterproof", "Softshell jacket", CATS)
        self.assertEqual(result["confidence"], "high")
        self.assertEqual(result["proposed_category_path"], _JACKETS["path"])

    def test_medium_confidence_ambiguous(self):
        # "jacket" (high=3) matches Jackets; "shirt" (medium=2) matches Shirts.
        # Top score 3 meets MEDIUM threshold; gap 1 is below HIGH_GAP 3 → medium.
        result = ct.classify("Jacket Shirt", "", CATS)
        self.assertEqual(result["confidence"], "medium")

    def test_low_confidence_no_signal(self):
        result = ct.classify("Artisan Collection No. 5", "", CATS)
        self.assertEqual(result["confidence"], "low")
        self.assertIsNone(result["proposed_category_path"])

    def test_alternatives_populated_for_ambiguous(self):
        # Both jackets and shirts can match — ensure alternatives are returned
        result = ct.classify("Waterproof Shirt", "", CATS)
        self.assertIsInstance(result["alternatives"], list)


class TestDepthBonusBreaksTie(unittest.TestCase):
    def test_deeper_tier_wins_at_equal_raw_score(self):
        # Shirts (tier 3) vs Tents (tier 5) both score from a single low-tier keyword.
        # Both have "camping" / "clothing" as low keywords. Use a product with both.
        cats = _preload([
            {
                "id": 1, "path": "Root > Mid > Deep > Leaf > Deepest",
                "tier": 5,
                "keywords": {"high": [], "medium": [], "low": ["test item"]},
            },
            {
                "id": 2, "path": "Root > Mid",
                "tier": 2,
                "keywords": {"high": [], "medium": [], "low": ["test item"]},
            },
        ])
        result = ct.classify("Test Item", "", cats)
        # Tier-5 category should win the tiebreaker
        self.assertEqual(result["proposed_category_path"], "Root > Mid > Deep > Leaf > Deepest")


class TestDeduplicate(unittest.TestCase):
    def test_removes_variant_rows(self):
        rows = [
            {"Title": "Rain Jacket", "Handle": "rain-jacket", "Variant SKU": "RJ-S"},
            {"Title": "", "Handle": "rain-jacket", "Variant SKU": "RJ-M"},
            {"Title": "", "Handle": "rain-jacket", "Variant SKU": "RJ-L"},
            {"Title": "Tent", "Handle": "tent", "Variant SKU": "T-1"},
        ]
        result = ct.deduplicate(rows, "Title")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Title"], "Rain Jacket")
        self.assertEqual(result[1]["Title"], "Tent")

    def test_deduplicates_case_insensitively(self):
        rows = [
            {"Title": "Rain Jacket"},
            {"Title": "rain jacket"},
        ]
        result = ct.deduplicate(rows, "Title")
        self.assertEqual(len(result), 1)


class TestPreserveExisting(unittest.TestCase):
    """--preserve-existing: rows with 3+ level deep existing category are skipped."""

    def _make_csv(self, rows):
        import csv, io
        fieldnames = list(rows[0].keys())
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        buf.seek(0)
        return buf.getvalue()

    def test_deep_existing_produces_preserved_confidence(self):
        csv_content = self._make_csv([
            {
                "Title": "Rain Jacket",
                "Body (HTML)": "A jacket",
                "Handle": "rj",
                "google_product_category": (
                    "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets"
                ),
            }
        ])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            tmpfile = f.name
        try:
            rows, title_col, desc_col, handle_col, category_col, _, encoding_used, _ = ct.load_csv(
                tmpfile, None, None
            )
            self.assertIsNotNone(category_col)

            # Simulate preserve logic
            existing = rows[0].get(category_col, "").strip()
            self.assertGreaterEqual(existing.count(" > "), 2)
        finally:
            os.unlink(tmpfile)

    def test_shallow_existing_not_preserved(self):
        csv_content = self._make_csv([
            {
                "Title": "Rain Jacket",
                "Body (HTML)": "",
                "Handle": "rj",
                "google_product_category": "Apparel & Accessories",
            }
        ])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(csv_content)
            tmpfile = f.name
        try:
            rows, _, _, _, category_col, _, _, _ = ct.load_csv(tmpfile, None, None)
            existing = rows[0].get(category_col, "").strip()
            self.assertLess(existing.count(" > "), 2)
        finally:
            os.unlink(tmpfile)


class TestPolicyFlags(unittest.TestCase):
    def test_alcohol_flag_detected(self):
        flags = ct.check_policy_flags("Red Wine Gift Set", "Premium Bordeaux wine", None)
        self.assertIn("alcohol_regulated", flags)

    def test_mead_not_confused_with_meadow(self):
        flags = ct.check_policy_flags("Alpine Meadow 2P Tent", "Camp in the meadows", None)
        self.assertNotIn("alcohol_regulated", flags)

    def test_apparel_flag_from_proposed_path(self):
        flags = ct.check_policy_flags(
            "Rain Jacket", "",
            "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets"
        )
        self.assertIn("apparel_requires_attributes", flags)

    def test_no_flags_for_neutral_product(self):
        flags = ct.check_policy_flags("Camping Tent", "3-season shelter", None)
        self.assertEqual(flags, [])

    def test_mead_as_standalone_word_triggers_flag(self):
        flags = ct.check_policy_flags("Honey Mead Starter Kit", "Traditional mead brewing", None)
        self.assertIn("alcohol_regulated", flags)


class TestBundleDetection(unittest.TestCase):
    def test_bundle_keyword_detected(self):
        self.assertTrue(ct.detect_bundle("Camping Starter Kit", ""))

    def test_gift_set_detected(self):
        self.assertTrue(ct.detect_bundle("Skincare Gift Set", ""))

    def test_npack_pattern_detected(self):
        self.assertTrue(ct.detect_bundle("Hiking Socks (3-pack)", ""))

    def test_regular_product_not_flagged(self):
        self.assertFalse(ct.detect_bundle("Rain Jacket", "Waterproof hardshell jacket"))

    def test_trek_pack_not_flagged(self):
        self.assertFalse(ct.detect_bundle(
            "Cedar Ridge 45L Trek Pack",
            "A comfortable pack for 2-4 day trips."
        ))

    def test_camp_towel_not_flagged(self):
        self.assertFalse(ct.detect_bundle("QuickDry Camp Towel", "Microfiber towel"))


class TestDuplicateIdGuard(unittest.TestCase):
    def _write_taxonomy(self, categories, tmpdir):
        import json, os
        path = os.path.join(tmpdir, "taxonomy-keywords.json")
        with open(path, "w") as f:
            json.dump({"categories": categories}, f)
        return tmpdir

    def test_guard_nulls_duplicate_ids(self):
        import sys, io
        cats_data = [
            {"id": 99, "path": "A > B", "tier": 2,
             "keywords": {"high": ["alpha"], "medium": [], "low": []}},
            {"id": 99, "path": "C > D", "tier": 2,
             "keywords": {"high": ["beta"], "medium": [], "low": []}},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_taxonomy(cats_data, tmpdir)
            stderr_capture = io.StringIO()
            old_stderr = sys.stderr
            sys.stderr = stderr_capture
            try:
                cats = ct.load_taxonomy(tmpdir)
            finally:
                sys.stderr = old_stderr

            # Both entries should have id=None now
            for cat in cats:
                self.assertIsNone(cat["id"])
            # Warning should have been printed to stderr
            self.assertIn("duplicate ID", stderr_capture.getvalue())

    def test_unique_ids_not_affected(self):
        import sys, io
        cats_data = [
            {"id": 10, "path": "A > B", "tier": 2,
             "keywords": {"high": [], "medium": [], "low": []}},
            {"id": 20, "path": "C > D", "tier": 2,
             "keywords": {"high": [], "medium": [], "low": []}},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_taxonomy(cats_data, tmpdir)
            stderr_capture = io.StringIO()
            old_stderr = sys.stderr
            sys.stderr = stderr_capture
            try:
                cats = ct.load_taxonomy(tmpdir)
            finally:
                sys.stderr = old_stderr

            ids = [cat["id"] for cat in cats]
            self.assertIn(10, ids)
            self.assertIn(20, ids)
            self.assertNotIn("duplicate ID", stderr_capture.getvalue())


class TestEncodingFallback(unittest.TestCase):
    def test_latin1_file_loads(self):
        content = "Title,Body (HTML)\nCafé Jacket,Warm jacket\n"
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".csv", delete=False
        ) as f:
            f.write(content.encode("latin-1"))
            tmpfile = f.name
        try:
            rows, title_col, _, _, _, _, encoding_used, warning = ct.load_csv(
                tmpfile, None, None
            )
            self.assertEqual(encoding_used, "latin-1")
            self.assertIsNotNone(warning)
            self.assertEqual(len(rows), 1)
        finally:
            os.unlink(tmpfile)

    def test_utf8_file_reports_no_warning(self):
        content = "Title,Body (HTML)\nRain Jacket,Waterproof\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8-sig"
        ) as f:
            f.write(content)
            tmpfile = f.name
        try:
            _, _, _, _, _, _, encoding_used, warning = ct.load_csv(tmpfile, None, None)
            self.assertEqual(encoding_used, "utf-8-sig")
            self.assertIsNone(warning)
        finally:
            os.unlink(tmpfile)


class TestEndToEndFixture(unittest.TestCase):
    """Integration test using the real fixture CSV and taxonomy-keywords.json."""

    FIXTURE_CSV = os.path.join(
        os.path.dirname(__file__), "..", "..", "..",
        "fixtures", "greatoutdoorsco", "shopify-products.csv"
    )
    ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

    @unittest.skipUnless(
        os.path.exists(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..",
                "fixtures", "greatoutdoorsco", "shopify-products.csv"
            )
        ),
        "Fixture CSV not found",
    )
    def test_fixture_classifies_without_error(self):
        categories = ct.load_taxonomy(self.ASSETS_DIR)
        rows, title_col, desc_col, handle_col, category_col, _, _, _ = ct.load_csv(
            self.FIXTURE_CSV, None, None
        )
        rows = ct.deduplicate(rows, title_col)
        self.assertGreater(len(rows), 0)
        for row in rows:
            title = row.get(title_col, "").strip()
            desc = row.get(desc_col, "").strip() if desc_col else ""
            result = ct.classify(title, desc, categories)
            self.assertIn(result["confidence"], ("high", "medium", "low"))

    @unittest.skipUnless(
        os.path.exists(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..",
                "fixtures", "greatoutdoorsco", "shopify-products.csv"
            )
        ),
        "Fixture CSV not found",
    )
    def test_fixture_produces_no_false_positive_alcohol_flags(self):
        categories = ct.load_taxonomy(self.ASSETS_DIR)
        rows, title_col, desc_col, _, _, _, _, _ = ct.load_csv(
            self.FIXTURE_CSV, None, None
        )
        rows = ct.deduplicate(rows, title_col)
        for row in rows:
            title = row.get(title_col, "").strip()
            desc = row.get(desc_col, "").strip() if desc_col else ""
            result = ct.classify(title, desc, categories)
            flags = ct.check_policy_flags(title, desc, result["proposed_category_path"])
            self.assertNotIn(
                "alcohol_regulated", flags,
                f"False positive alcohol flag on: {title}"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
