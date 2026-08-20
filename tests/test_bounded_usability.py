import tempfile
import unittest
from pathlib import Path
import yaml
from scripts import run_bounded_usability as brp

ROOT=Path(__file__).resolve().parents[1]
class BoundedUsabilityTests(unittest.TestCase):
    def test_frozen_profile_has_twelve_distinct_fixtures(self):
        data=yaml.safe_load(brp.SCENARIOS.read_text())
        self.assertTrue(data['frozen'])
        self.assertEqual(len(data['scenarios']),12)
        self.assertEqual(len({s['id'] for s in data['scenarios']}),12)
        for scenario in data['scenarios']:
            self.assertTrue((ROOT/scenario['fixture']).is_dir())
            self.assertIn('validity boundary',scenario['prompt'].lower())
    def test_blind_sample_id_is_deterministic(self):
        self.assertEqual(brp.sid('run-1'),brp.sid('run-1'))
        self.assertNotEqual(brp.sid('run-1'),brp.sid('run-2'))
    def test_score_schema_is_strict(self):
        import json
        from jsonschema import Draft202012Validator
        schema=json.loads(brp.SCHEMA.read_text())
        self.assertFalse(list(Draft202012Validator(schema).iter_errors({}))) if False else self.assertTrue(list(Draft202012Validator(schema).iter_errors({})))
    def test_evaluation_tooling_is_not_packaged(self):
        manifest=yaml.safe_load((ROOT/'manifest.yaml').read_text())
        includes=manifest['package']['include']
        self.assertFalse(any(str(item).startswith('evaluations') for item in includes))
        self.assertNotIn('scripts/run_bounded_usability.py',includes)
if __name__=='__main__': unittest.main()
