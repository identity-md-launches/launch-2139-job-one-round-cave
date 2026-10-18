#!/usr/bin/env python3
"""Check references in an Offline Resolver catalog without resolving it."""
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESOLVER = HERE.parent / 'offline-resolver' / 'resolve.py'
spec = importlib.util.spec_from_file_location('line4_offline_resolver', RESOLVER)
resolver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolver)


def inspect_catalog(catalog):
    """Validate the map schema, then list absent target packages.

    A missing reference is reported even if it belongs to a release the solver
    might never select. This is a catalog quality check, not a satisfiability
    claim. Canonical package names and constraints come from Offline Resolver.
    """
    if isinstance(catalog, dict) and 'roots' not in catalog:
        return inspect_legacy_catalog(catalog)
    packages, roots = resolver.validate(catalog)
    missing = []
    for target in sorted(roots):
        if target not in packages:
            missing.append({'source': 'root', 'dependency': target,
                            'constraint': roots[target]})
    for package in sorted(packages):
        for release in sorted(packages[package], key=resolver.version):
            for target, constraint in sorted(packages[package][release].items()):
                if target not in packages:
                    missing.append({'source': package + '@' + release,
                                    'dependency': target, 'constraint': constraint})
    return {'packages': len(packages),
            'releases': sum(map(len, packages.values())),
            'missing_dependency_targets': missing,
            'healthy': not missing}


def inspect_legacy_catalog(catalog):
    """Keep the earlier list-based catalog form usable for its callers."""
    if set(catalog) != {'packages'} or not isinstance(catalog['packages'], dict):
        raise resolver.Invalid('legacy catalog must contain only packages')
    packages = catalog['packages']
    if any(not isinstance(name, str) or not name.strip() or
           not isinstance(versions, dict) for name, versions in packages.items()):
        raise resolver.Invalid('package names and release maps must be non-empty objects')
    missing = []
    releases = 0
    for name, versions in sorted(packages.items()):
        if any(not isinstance(version, str) or not version.strip() or
               not isinstance(metadata, dict) for version, metadata in versions.items()):
            raise resolver.Invalid('release labels and metadata must be non-empty objects')
        for version, metadata in sorted(versions.items()):
            if set(metadata) - {'dependencies'}:
                raise resolver.Invalid('legacy release metadata supports only dependencies lists')
            dependencies = metadata.get('dependencies', [])
            if (not isinstance(dependencies, list) or
                    any(not isinstance(d, str) or not d.strip() for d in dependencies)):
                raise resolver.Invalid('dependencies must be a list of strings')
            releases += 1
            for dependency in dependencies:
                target = dependency.split()[0]
                if target not in packages:
                    missing.append({'package': name, 'version': version,
                                    'dependency': target})
    return {'packages': len(packages), 'releases': releases,
            'missing_dependency_targets': missing, 'healthy': not missing}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print('usage: health.py demo|CATALOG.json', file=sys.stderr)
        return 2
    try:
        path = (HERE.parent / 'offline-resolver' / 'examples' / 'requests.json'
                if argv[0] == 'demo' else argv[0])
        catalog = resolver.load(path)
        result = inspect_catalog(catalog)
    except (resolver.Invalid, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({'error': str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result['healthy'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
