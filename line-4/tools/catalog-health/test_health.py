import copy
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('catalog_health', HERE / 'health.py')
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


class CatalogHealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = health.resolver.load(
            HERE.parent / 'offline-resolver' / 'examples' / 'requests.json')

    def test_real_requests_projection_is_referentially_complete(self):
        result = health.inspect_catalog(self.requests)
        self.assertEqual(result['packages'], 5)
        self.assertEqual(result['releases'], 10)
        self.assertEqual(result['missing_dependency_targets'], [])
        self.assertTrue(result['healthy'])

    def test_missing_target_in_real_dependency_map_is_reported(self):
        catalog = copy.deepcopy(self.requests)
        catalog['packages']['requests']['2.32.5']['missing-package'] = '>=1'
        report = health.inspect_catalog(catalog)
        self.assertFalse(report['healthy'])
        self.assertEqual(report['missing_dependency_targets'], [
            {'source': 'requests@2.32.5', 'dependency': 'missing-package',
             'constraint': '>=1'}])
        self.assertEqual(health.resolver.solve(catalog)['status'], 'unsatisfiable')

    def test_missing_root_is_reported(self):
        catalog = copy.deepcopy(self.requests)
        catalog['roots']['Absent_Package'] = '*'
        report = health.inspect_catalog(catalog)
        self.assertEqual(report['missing_dependency_targets'], [
            {'source': 'root', 'dependency': 'absent-package', 'constraint': '*'}])

    def test_name_alias_matches_existing_package(self):
        catalog = copy.deepcopy(self.requests)
        catalog['packages']['requests']['2.32.5']['CHARSET_normalizer'] = '<4,>=2'
        del catalog['packages']['requests']['2.32.5']['charset-normalizer']
        self.assertTrue(health.inspect_catalog(catalog)['healthy'])

    def test_list_schema_is_rejected_instead_of_silently_ignored(self):
        catalog = copy.deepcopy(self.requests)
        catalog['packages']['requests']['2.32.5'] = {
            'dependencies': ['missing-package >=1']}
        with self.assertRaises(health.resolver.Invalid):
            health.inspect_catalog(catalog)

    def test_invalid_constraint_is_rejected(self):
        catalog = copy.deepcopy(self.requests)
        catalog['packages']['requests']['2.32.5']['urllib3'] = '^2'
        with self.assertRaises(health.resolver.Invalid):
            health.inspect_catalog(catalog)

    def test_earlier_list_schema_still_works(self):
        catalog = {'packages': {'alpha': {'1': {'dependencies': ['beta >=1']}},
                                'beta': {'1': {'dependencies': []}}}}
        self.assertTrue(health.inspect_catalog(catalog)['healthy'])
        del catalog['packages']['beta']
        self.assertEqual(health.inspect_catalog(catalog)['missing_dependency_targets'],
                         [{'package': 'alpha', 'version': '1', 'dependency': 'beta'}])


if __name__ == '__main__':
    unittest.main()
