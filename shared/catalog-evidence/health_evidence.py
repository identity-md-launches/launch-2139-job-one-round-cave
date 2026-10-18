#!/usr/bin/env python3
"""Search exact citations in regenerated finite-catalog reference diagnostics."""
import argparse
import json
from pathlib import Path
import sys

import evidence
import health

HERE = Path(__file__).resolve().parent


def inspect(catalog, query, limit=5):
    # Validate once with the same numeric grammar as the recipient's resolver.
    normalized = evidence.delta.normalized(catalog)
    result = health.inspect_catalog(normalized)
    rows = [
        '# Catalog reference inspection',
        'Normalized catalog SHA-256: ' + evidence.delta.digest(normalized),
        'Scope: every root and every release, including unselected releases.',
        'This checks target package existence only, not compatible versions or installability.',
        'Healthy means no missing target names; it is not a resolver result.',
        '',
        'Packages: ' + str(result['packages']),
        'Releases: ' + str(result['releases']),
        'Reference targets complete: ' + str(result['healthy']).lower(),
    ]
    for item in result['missing_dependency_targets']:
        rows.append('Missing dependency target: ' + evidence.quoted(item['dependency'])
                    + '; source ' + evidence.quoted(item['source'])
                    + '; constraint ' + evidence.quoted(item['constraint']))
    if result['healthy']:
        rows.append('No missing dependency targets in this finite catalog.')
    text = '\n'.join(rows) + '\n'
    source = {'path': 'catalog-health.md', 'text': text,
              'sha256': evidence.search.digest(text.encode('utf-8'))}
    index = {'format': evidence.search.FORMAT, 'documents': [source]}
    hits = evidence.search.search_snapshot(index, query, limit=limit)
    return {'format': 'catalog-health-evidence/v1',
            'catalog_sha256': evidence.delta.digest(normalized),
            'health': result, 'documents': [source], 'search': hits,
            'trust': 'Exact citations identify regenerated diagnostic bytes. '
                     'They do not authenticate catalogs or prove compatibility, '
                     'freshness, publisher trust, or factual support.'}


def demo(query='missing dependency'):
    # Real inherited Requests projection, with an explicitly injected broken edge
    # in memory. This is a regression trial, never a claim about PyPI metadata.
    catalog = evidence.delta.resolver.load(HERE / 'examples/before.json')
    baseline = inspect(catalog, query)
    catalog['packages']['requests']['2.32.5']['missing-package'] = '>=1'
    broken = inspect(catalog, query)
    return {'baseline': baseline, 'injected_missing_target': broken,
            'demo': 'Historical Requests projection plus one injected missing-package '
                    'edge in memory; no registry or current package claim.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    show = sub.add_parser('demo')
    show.add_argument('query', nargs='?', default='missing dependency')
    scan = sub.add_parser('inspect')
    scan.add_argument('catalog')
    scan.add_argument('query')
    scan.add_argument('--limit', type=int, default=5)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo(args.query)
            status = 0  # A demonstration intentionally includes a broken catalog.
        else:
            result = inspect(evidence.delta.resolver.load(args.catalog), args.query, args.limit)
            # Missing references take precedence over an empty lexical query result.
            status = 1 if not result['health']['healthy'] else 0
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return status
    except (evidence.delta.resolver.Invalid, health.resolver.Invalid,
            evidence.search.SearchError, OSError, UnicodeError,
            ValueError, RecursionError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
