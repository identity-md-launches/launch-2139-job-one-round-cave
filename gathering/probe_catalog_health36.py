"""Recheck the inherited missing-target regression on the repaired map schema."""
import importlib.util
import json
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    sample = json.loads(Path('shared/catalog-evidence/examples/before.json').read_text())
    sample['packages']['requests']['2.32.5']['missing-package'] = '>=1'
    health = load('catalog_health_probe', 'line-4/tools/catalog-health/health.py')
    resolver = load('resolver_probe', 'line-4/tools/offline-resolver/resolve.py')
    observed = health.inspect_catalog(sample)
    solved = resolver.solve(sample)
    rejected = solved['status'] == 'unsatisfiable'
    reason = solved.get('conflict', {}).get('package')
    assert not observed['healthy'] and observed['missing_dependency_targets'] == [{'source':'requests@2.32.5','dependency':'missing-package','constraint':'>=1'}]
    assert rejected and 'missing-package' in reason
    finding = {'source': 'historical Requests metadata projection with one absent dependency target',
               'catalog_health': observed, 'resolver_rejected': rejected,
               'resolver_reason': reason,
               'finding_status': 'fixed in inherited line tree', 'observation': 'Catalog Health now validates resolver maps and reports the injected missing target; resolver also rejects it.'}
    Path('gathering/catalog-health-probe-36.json').write_text(json.dumps(finding, indent=2) + '\n')
    print(json.dumps(finding, indent=2))


if __name__ == '__main__':
    main()
