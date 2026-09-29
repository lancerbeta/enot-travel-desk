"""Registry routing priors. No live provider calls."""

import unittest

from enotcheck.registry import CORE_FAMILIES, admits, load_registry, source_index, validate_registry


class SourceRegistry(unittest.TestCase):
    def setUp(self):
        self.data = load_registry()
        self.sources = source_index(self.data)

    def test_registry_is_internally_consistent(self):
        errors = validate_registry(self.data)
        self.assertEqual(errors, [])

    def test_every_core_family_keeps_a_baseline_without_accelerators(self):
        for name in CORE_FAMILIES:
            spec = self.data["families"][name]
            self.assertIn(spec["baseline"], self.sources)
            self.assertFalse(self.sources[spec["baseline"]]["optional"])
            self.assertFalse(self.sources[spec["direct"]]["optional"])
            self.assertFalse(self.sources[spec["fallback"]]["optional"])
            for accelerator in spec["accelerators"]:
                self.assertTrue(self.sources[accelerator]["optional"])
                self.assertNotEqual(accelerator, spec["baseline"])

    def test_review_does_not_prove_an_official_rule(self):
        editorial = self.sources["local_discovery.editorial"]
        self.assertIn("review", editorial["roles"])
        self.assertFalse(admits(editorial, "official_rule"))

    def test_cached_discovery_price_is_not_current_inventory(self):
        cached = self.sources["air.aviasales_data_api"]
        self.assertEqual(cached["offer_kind"], "cached")
        self.assertFalse(admits(cached, "current_inventory"))

    def test_write_capable_channel_does_not_book_by_default(self):
        partner = self.sources["stays.partner_api"]
        self.assertTrue(partner["write_capable"])
        self.assertFalse(admits(partner, "external_write"))
        self.assertEqual(partner["external_actions_default"], "none")

    def test_registry_does_not_store_trip_prices(self):
        text = "\n".join(
            str(source)
            for source in self.data["runtime_sources"]
        )
        self.assertNotIn("live_price", text)
        self.assertNotIn("48000", text)
        self.assertEqual(validate_registry(self.data), [])


if __name__ == "__main__":
    unittest.main()
