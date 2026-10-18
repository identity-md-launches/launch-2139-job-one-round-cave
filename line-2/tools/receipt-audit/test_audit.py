import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tested_receipt_audit', HERE / 'audit.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.bundle = t.w.load_bundle(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json')
        self.layout = t.source.storage.load_layout(HERE.parent / 'storage-fields/pool-layout.json')
        self.saved = t.load_receipt(HERE / 'historical-receipt.json')

    def check(self, saved=None, **kwargs):
        return t.audit(self.saved if saved is None else saved, self.bundle,
                       kwargs.pop('root', t.w.DEMO_ROOT),
                       kwargs.pop('address', t.w.POOL_MANAGER),
                       kwargs.pop('layout', self.layout), **kwargs)

    def test_real_saved_receipt(self):
        result = self.check()
        self.assertTrue(result['verified'])
        self.assertEqual(result['fieldCount'], 5)
        self.assertEqual(self.saved['slots'][0]['fields'][-1]['valueDecimal'], '12500')

    def test_tampering_and_rehashing_does_not_pass(self):
        self.saved['slots'][0]['fields'][-1]['valueDecimal'] = '1'
        self.saved.pop('receiptSha256')
        self.saved['receiptSha256'] = hashlib.sha256(t.canonical(self.saved)).hexdigest()
        with self.assertRaisesRegex(t.w.Invalid, 'differs from reverified'):
            self.check()

    def test_every_core_field_is_bound(self):
        for key in self.saved:
            changed = copy.deepcopy(self.saved)
            changed[key] = None
            with self.subTest(key=key), self.assertRaises(t.w.Invalid):
                self.check(changed)

    def test_json_types_are_exact(self):
        for path in ('verified', 'storageExists'):
            changed = copy.deepcopy(self.saved)
            if path == 'verified':
                changed[path] = 1
            else:
                changed['slots'][0][path] = 1
            with self.subTest(path=path), self.assertRaises(t.w.Invalid):
                self.check(changed)

    def test_unknown_or_missing_field_rejected(self):
        for changed in ({**self.saved, 'extra': 'claim'},
                        {k: v for k, v in self.saved.items() if k != 'address'}):
            with self.assertRaises(t.w.Invalid):
                self.check(changed)

    def test_demo_text_is_not_evidence(self):
        self.assertEqual(self.check(), self.check({**self.saved, 'demo': 'untrusted text'}))
        with self.assertRaises(t.w.Invalid):
            self.check({**self.saved, 'demo': True})

    def test_root_and_address_are_external(self):
        for kwargs in ({'root': '0x' + '11' * 32}, {'address': t.w.ZTO}):
            with self.subTest(kwargs=kwargs), self.assertRaises(t.w.Invalid):
                self.check(**kwargs)

    def test_caller_layout_is_bound(self):
        changed = copy.deepcopy(self.layout)
        changed['slots'][0]['fields'][-1]['name'] = 'renamedFee'
        with self.assertRaises(t.w.Invalid):
            self.check(layout=changed)

    def test_broken_proof_rejected(self):
        self.bundle['proof']['accountProof'] = []
        with self.assertRaises(t.w.Invalid):
            self.check()

    def test_optional_independent_digest(self):
        self.assertTrue(self.check(expected_digest=self.saved['receiptSha256'])['digestPinned'])
        for digest in ('0' * 64, 'A' * 64, True, 'short'):
            with self.subTest(digest=digest), self.assertRaises(t.w.Invalid):
                self.check(expected_digest=digest)

    def test_duplicate_json_and_size_limit(self):
        with tempfile.TemporaryDirectory(dir=HERE) as folder:
            path = Path(folder) / 'input.json'
            for raw in (b'{"verified":true,"verified":false}', b' ' * 65537, b'{"x":NaN}'):
                path.write_bytes(raw)
                with self.assertRaises((t.w.Invalid, ValueError)):
                    t.load_receipt(path)

    def test_no_input_mutation(self):
        before = copy.deepcopy((self.saved, self.bundle, self.layout))
        self.check()
        self.assertEqual(before, (self.saved, self.bundle, self.layout))

    def test_cli_demo_and_rejection(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(t.main(['demo']), 0)
        self.assertTrue(json.loads(out.getvalue())['verified'])
        with contextlib.redirect_stderr(io.StringIO()) as err:
            status = t.main(['check', str(HERE / 'historical-receipt.json'),
                             str(HERE.parent / 'state-witness/examples/zto-pool-mainnet.json'),
                             str(HERE.parent / 'storage-fields/pool-layout.json'),
                             '--state-root', '0x' + '11' * 32, '--address', t.w.POOL_MANAGER])
        self.assertEqual(status, 1)
        self.assertFalse(json.loads(err.getvalue())['verified'])


if __name__ == '__main__':
    unittest.main()
