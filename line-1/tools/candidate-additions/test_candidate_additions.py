"""Behavior checks, including a real inherited documentation trial."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('candidate_additions_test',
    Path(__file__).with_name('candidate_additions.py'))
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class CandidateTests(unittest.TestCase):
    def row(self, base, ours, theirs, candidate):
        return audit.audit_candidate('x', base, ours, theirs, candidate)

    def test_demo(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(audit.main(['--demo']), 0)

    def test_both_contributors_and_symmetry(self):
        a = self.row('base\n', 'base\nleft\n', 'base\nright\n', 'base\n')
        b = self.row('base\n', 'base\nright\n', 'base\nleft\n', 'base\n')
        self.assertEqual(len(a['missing_lines']), 2)
        self.assertEqual([r['line_sha256'] for r in a['missing_lines']],
                         [r['line_sha256'] for r in b['missing_lines']])

    def test_existing_occurrence_cannot_mask_duplicate_addition(self):
        row = self.row('a\n', 'a\na\n', 'a\n', 'a\n')
        self.assertEqual(row['missing_lines'][0]['required_occurrences'], 2)
        self.assertEqual(row['missing_lines'][0]['candidate_occurrences'], 1)

    def test_shared_addition_not_summed(self):
        self.assertEqual(self.row('', 'a\n', 'a\n', 'a\n')['status'], 'checked')
        self.assertEqual(self.row('', 'a\na\n', 'a\n', 'a\n')['status'], 'review')

    def test_reorder_and_net_zero_are_out_of_scope(self):
        self.assertEqual(self.row('a\nb\n', 'b\na\n', 'a\nb\n', 'a\nb\n')['status'], 'checked')

    def test_missing_candidate_not_skipped(self):
        self.assertEqual(self.row('a\n', 'a\nb\n', 'a\n', None)['status'], 'review')
        self.assertEqual(self.row('a\n', None, 'a\n', None)['status'], 'checked')

    def test_empty_file_presence(self):
        self.assertTrue(self.row(None, '', None, None)['missing_added_file'])
        self.assertEqual(self.row(None, '', None, '')['status'], 'checked')
        self.assertEqual(self.row('', '', '', None)['status'], 'checked')

    def test_exact_unicode_and_newlines(self):
        for line in ('é\r\n', 'é\n', 'é'):
            self.assertEqual(self.row('', line, '', line)['status'], 'checked')
            self.assertEqual(self.row('', line, '', None)['status'], 'review')
        self.assertEqual(self.row('', 'é\r\n', '', 'é\n')['status'], 'review')

    def test_path_collision_and_descendants(self):
        report = audit.inspect([
            {'files': {'x': ''}, 'directories': set()},
            {'files': {'x/y': 'a'}, 'directories': {'x'}},
            {'files': {}, 'directories': set()},
            {'files': {'x/y': 'a'}, 'directories': {'x'}}])
        self.assertEqual(report['counts']['blocked'], 2)
        self.assertTrue(report['needs_review'])

    def test_real_document_trial_and_candidate_manifest(self):
        # All generated files remain within the explicitly permitted scratch area.
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            paths = [Path(folder) / side for side in audit.SIDES]
            base = Path('line-1/tools/threeway/README.md').read_text()
            ours = base + '\nRetain the input fingerprints.\n'
            theirs = base + '\nReview every conflict.\n'
            good = ours + '\nReview every conflict.\n'
            for path, content in zip(paths, (base, ours, theirs, good)):
                path.mkdir()
                (path / 'README.md').write_text(content)
            before = [(p / 'README.md').read_bytes() for p in paths]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(audit.main(list(map(str, paths))), 0)
            report = json.loads(out.getvalue())
            self.assertEqual(before, [(p / 'README.md').read_bytes() for p in paths])
            (paths[3] / 'README.md').write_text(ours)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit.main(list(map(str, paths))), 1)
            changed = audit.from_directories(paths)
            self.assertNotEqual(report['inputs']['candidate'], changed['inputs']['candidate'])
            self.assertEqual(changed['files'][0]['missing_lines'][0]['added_by'], ['theirs'])

    def test_symlink_rejection_no_partial_report(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            root = Path(folder)
            (root / 'link').symlink_to('missing')
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(audit.main([str(root)] * 4), 2)
            self.assertEqual(out.getvalue(), '')
            self.assertIn('symlink', err.getvalue())

    def test_counts_and_no_source_text(self):
        text = 'distinctive hidden source\n'
        report = audit.inspect([{'files': files, 'directories': set()} for files in
            ({}, {'x': text}, {}, {})])
        self.assertEqual(report['counts']['review'], 1)
        self.assertNotIn(text.strip(), json.dumps(report))

    def test_four_trees_required(self):
        for function in (audit.inspect, audit.from_directories):
            with self.assertRaises(ValueError):
                function([])


if __name__ == '__main__':
    unittest.main()
