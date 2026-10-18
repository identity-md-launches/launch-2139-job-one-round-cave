#!/usr/bin/env python3
"""Reverify a saved Proof Receipt against caller-selected evidence and anchors."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('receipt_audit_source', HERE.parent / 'proof-receipt/receipt.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
w = source.w
MAX_RECEIPT = 65536


def canonical(value):
    # Comparing canonical bytes also distinguishes JSON true from numeric 1.
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def load_receipt(path):
    with w.workspace_path(path).open('rb') as stream:
        raw = stream.read(MAX_RECEIPT + 1)
    w.require(len(raw) <= MAX_RECEIPT, 'receipt exceeds 64 KiB')
    return w.parse_json(raw)


def audit(saved, bundle, state_root, address, layout, expected_digest=None):
    """Never take the root, address or layout from the untrusted saved receipt."""
    w.require(isinstance(saved, dict), 'receipt must be an object')
    if expected_digest is not None:
        w.require(isinstance(expected_digest, str) and
                  re.fullmatch('[0-9a-f]{64}', expected_digest) is not None,
                  'expected digest must be 64 lowercase hex digits')
    core = dict(saved)
    # The producer's demo annotation is explicitly untrusted and not hashed.
    if 'demo' in core:
        w.require(isinstance(core.pop('demo'), str), 'demo annotation must be text')
    regenerated = source.make_receipt(bundle, state_root, address, layout)
    w.require(set(core) == set(regenerated), 'receipt has missing or unknown fields')
    w.require(canonical(core) == canonical(regenerated),
              'saved receipt differs from reverified evidence')
    digest = regenerated['receiptSha256']
    w.require(expected_digest is None or digest == expected_digest,
              'receipt differs from independently pinned digest')
    return {
        'format': 'receipt-audit/1', 'verified': True,
        'receiptSha256': digest, 'stateRoot': regenerated['stateRoot'],
        'address': regenerated['address'], 'layoutSha256': regenerated['layoutSha256'],
        'slotCount': len(regenerated['slots']),
        'fieldCount': sum(len(row['fields']) for row in regenerated['slots']),
        'digestPinned': expected_digest is not None,
        'trust': 'Saved receipt matches freshly verified evidence against the supplied root, address and layout. Root authentication, layout meaning, freshness and consensus remain caller responsibilities. Demo text is ignored.',
    }


def demo():
    bundle = w.load_bundle(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json')
    layout = source.storage.load_layout(HERE.parent / 'storage-fields/pool-layout.json')
    saved = load_receipt(HERE / 'historical-receipt.json')
    result = audit(saved, bundle, w.DEMO_ROOT, w.POOL_MANAGER, layout)
    result['demo'] = 'Historical real ZTO/IMD pool at block 26212390; fixed RPC-observed root is illustrative, not independently authenticated.'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('demo')
    check = sub.add_parser('check')
    check.add_argument('receipt')
    check.add_argument('witness')
    check.add_argument('layout')
    check.add_argument('--state-root', required=True)
    check.add_argument('--address', required=True)
    check.add_argument('--expected-digest')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            result = audit(load_receipt(args.receipt), w.load_bundle(args.witness),
                           args.state_root, args.address,
                           source.storage.load_layout(args.layout), args.expected_digest)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except w.Invalid as error:
        print(json.dumps({'verified': False, 'error': str(error)}), file=sys.stderr)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, OverflowError):
        print(json.dumps({'verified': False, 'error': 'Unreadable or malformed input.'}), file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
