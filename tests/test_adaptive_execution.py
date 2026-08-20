import tempfile
import unittest
from pathlib import Path

from scripts.adaptive_execution import (
    EvidenceItem, EvidenceSufficiency, Escalation, Level, Rating, SourceCache,
    deduplicate_evidence, historical_memory_is_material,
)


class AdaptiveExecutionTests(unittest.TestCase):
    def test_absence_of_contradiction_does_not_support_affirmative_yes(self):
        evidence = EvidenceSufficiency(False, "SUFFICIENT", True, "SUFFICIENT")
        self.assertFalse(evidence.supports_yes())

    def test_missing_production_evidence_preserves_maybe(self):
        evidence = EvidenceSufficiency(True, "LIMITED", True, "SUFFICIENT")
        self.assertFalse(evidence.supports_yes())

    def test_incomplete_security_search_cannot_support_no_vulnerability_yes(self):
        evidence = EvidenceSufficiency(False, "LIMITED", True, "LIMITED", False)
        self.assertFalse(evidence.supports_yes(bounded_negative=True))

    def test_complete_bounded_manifest_search_can_support_scoped_absence(self):
        evidence = EvidenceSufficiency(False, "SUFFICIENT", True, "SUFFICIENT", True)
        self.assertTrue(evidence.supports_yes(bounded_negative=True))

    def test_low_information_gain_never_escalates(self):
        escalation = Escalation(Level.EVALUATE, Level.SPECIALIZE, ("INSUFFICIENT_EVIDENCE",), Rating.LOW, Rating.LOW)
        self.assertFalse(escalation.justified())

    def test_material_high_gain_escalation_is_justified(self):
        escalation = Escalation(Level.EVALUATE, Level.SPECIALIZE, ("SECURITY_RELEVANT",), Rating.HIGH, Rating.HIGH)
        self.assertTrue(escalation.justified(material=True))

    def test_unknown_reason_cannot_escalate(self):
        escalation = Escalation(Level.EVALUATE, Level.SPECIALIZE, ("STAGE_UNUSED",), Rating.HIGH, Rating.LOW)
        self.assertFalse(escalation.justified())

    def test_unchanged_source_is_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.txt"
            path.write_text("evidence", encoding="utf-8")
            cache = SourceCache()
            _, first_hit = cache.read(path)
            _, second_hit = cache.read(path)
            self.assertFalse(first_hit)
            self.assertTrue(second_hit)
            self.assertEqual(sum(cache.reads.values()), 1)

    def test_common_ancestry_is_not_independent_corroboration(self):
        items = [
            EvidenceItem("E1", "a.md", "1", "same claim", "DIRECT", "origin"),
            EvidenceItem("E2", "b.md", "1", "same claim", "COPIED", "origin"),
        ]
        self.assertEqual(len(deduplicate_evidence(items)), 1)

    def test_historical_memory_requires_current_verification(self):
        historical = EvidenceItem("E1", "memory", "finding", "feature absent", "MEMORY", memory_status="HISTORICAL")
        current = EvidenceItem("E2", "source", "line 1", "feature absent", "DIRECT", memory_status="VERIFIED_CURRENT")
        self.assertFalse(historical_memory_is_material(historical))
        self.assertTrue(historical_memory_is_material(current))


if __name__ == "__main__":
    unittest.main()
