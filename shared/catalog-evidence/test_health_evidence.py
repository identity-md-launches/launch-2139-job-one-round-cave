"""Behavioral regression checks for the repaired reference-to-citation bridge."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import health_evidence as h


class HealthEvidenceTests(unittest.TestCase):
    def catalog(self):
        return h.evidence.delta.resolver.load(h.HERE / 'examples/before.json')

    def test_inherited_real_catalog_then_injected_regression(self):
        result = h.demo()
        self.assertTrue(result['baseline']['health']['healthy'])
        broken = result['injected_missing_target']
        self.assertFalse(broken['health']['healthy'])
        self.assertEqual(broken['health']['missing_dependency_targets'], [
            {'source': 'requests@2.32.5', 'dependency': 'missing-package', 'constraint': '>=1'}])
        self.assertTrue(broken['search']['hits'])

    def test_exact_citation_bytes(self):
        result = h.demo()['injected_missing_target']
        doc = result['documents'][0]
        self.assertEqual(doc['sha256'], hashlib.sha256(doc['text'].encode()).hexdigest())
        for hit in result['search']['hits']:
            self.assertEqual(hit['path'], 'catalog-health.md')
            self.assertEqual(hit['text'], '\n'.join(doc['text'].splitlines()[hit['line_start']-1:hit['line_end']]))
            self.assertEqual(hit['sha256'], doc['sha256'])
            self.assertFalse(hit['source_verified'])

    def test_root_and_unselected_release_are_both_inspected(self):
        catalog = {'roots': {'app': '==1', 'Absent_Root': '*'},
                   'packages': {'app': {'1': {}, '2': {'Absent_Edge': '>=2'}}}}
        result = h.inspect(catalog, 'absent')
        self.assertEqual(result['health']['missing_dependency_targets'], [
            {'source': 'root', 'dependency': 'absent-root', 'constraint': '*'},
            {'source': 'app@2', 'dependency': 'absent-edge', 'constraint': '>=2'}])

    def test_healthy_is_not_satisfiable(self):
        catalog = {'roots': {'app': '*'},
                   'packages': {'app': {'1': {'dep': '>=2'}}, 'dep': {'1': {}}}}
        self.assertTrue(h.inspect(catalog, 'healthy')['health']['healthy'])
        self.assertEqual(h.evidence.delta.resolver.solve(catalog)['status'], 'unsatisfiable')

    def test_determinism_immutability_and_identity(self):
        original = self.catalog()
        saved = copy.deepcopy(original)
        a = h.inspect(original, 'requests')
        b = h.inspect(json.loads(json.dumps(original), object_pairs_hook=lambda p: dict(reversed(p))), 'requests')
        self.assertEqual(a, b)
        self.assertEqual(original, saved)
        original['roots']['requests'] = '>=2.32.5'
        self.assertNotEqual(a['catalog_sha256'], h.inspect(original, 'requests')['catalog_sha256'])

    def test_bad_catalog_query_and_limits_rejected(self):
        for catalog in ({}, {'packages': {'a': {'1': {'dependencies': ['x']}}}}):
            with self.assertRaises(ValueError):
                h.inspect(catalog, 'missing')
        for query, limit in (('', 5), ('a', 0)):
            with self.assertRaises(ValueError):
                h.inspect(self.catalog(), query, limit)

    def test_cli_health_status_independent_of_search_hits(self):
        for args, expected in [(['demo'], 0),
                               (['inspect', str(h.HERE / 'examples/before.json'), 'zzznomatchzzz'], 0),
                               (['inspect', str(h.HERE / 'examples/before.json'), 'x', '--limit', '0'], 2),
                               (['inspect', '../outside.json', 'x'], 2)]:
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(h.main(args), expected)
            self.assertIsInstance(json.loads(out.getvalue() or err.getvalue()), dict)

    def test_source_and_adaptation_provenance(self):
        item = json.loads((h.HERE / 'HEALTH-PROVENANCE.json').read_text())
        source = Path(item['source']).read_bytes()
        copied = (h.HERE / item['copy']).read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), item['source_sha256'])
        self.assertEqual(hashlib.sha256(copied).hexdigest(), item['copy_sha256'])
        expected = source.decode().replace("RESOLVER = HERE.parent / 'offline-resolver' / 'resolve.py'", "RESOLVER = HERE / 'resolve.py'").replace("HERE.parent / 'offline-resolver' / 'examples' / 'requests.json'", "HERE / 'examples' / 'before.json'")
        self.assertEqual(expected.encode(), copied)

    def test_cli_missing_reference_is_nonzero_even_with_no_hits(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            path = Path(folder) / 'catalog.json'
            catalog = self.catalog()
            catalog['packages']['requests']['2.32.5']['missing-package'] = '>=1'
            path.write_text(json.dumps(catalog))
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = h.main(['inspect', str(path), 'zzznomatchzzz'])
            self.assertEqual(code, 1)
            result = json.loads(out.getvalue())
            self.assertFalse(result['health']['healthy'])
            self.assertEqual(result['search']['hits'], [])


if __name__ == '__main__':
    unittest.main()
