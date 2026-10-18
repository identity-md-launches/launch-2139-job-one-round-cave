"""Reproduce Citation Report's source-path loss without editing line inputs."""
import importlib.util
import json
from pathlib import Path
import tempfile


def main():
    source = Path('line-3/tools/citation-report/report.py')
    spec = importlib.util.spec_from_file_location('probe_citation_report', source)
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    observations = {'demo': report.demo()}
    scratch = Path('test/scratch')
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch, prefix='citation-report36-') as temp:
        root = Path(temp) / 'docs'
        root.mkdir()
        raw = Path('line-3/tools/evidence-search/examples/docs/zto.md').read_bytes()
        (root / 'zto.md').write_bytes(raw)
        ledger = {'format': report.ledger.FORMAT, 'entries': [
            {'id': 'zto', 'anchor': report.ledger.anchor.capture(root, 'zto.md', 3, 6)}]}
        saved = Path(temp) / 'ledger.json'
        saved.write_text(json.dumps(ledger))
        observations['unchanged'] = report.report(root, saved)
        (root / 'zto.md').write_bytes(b'# Reading copy\n\n' + raw)
        observations['relocated'] = report.report(root, saved)
    assert observations['unchanged']['all_unchanged'] is True
    assert observations['relocated']['all_unchanged'] is False
    assert observations['relocated']['review_count'] == 1
    assert observations['relocated']['entries'][0]['status'] == 'relocated'
    assert observations['relocated']['entries'][0]['source'] == ''
    result = {'tool': str(source), 'observations': observations, 'findings': [{
        'severity': 'medium',
        'summary': 'Citation Report emits empty source for valid citations.',
        'expected_source': 'zto.md', 'observed_source': '',
        'cause': 'Reanchor results have no top-level path; result.get("path", "") loses the ledger anchor path.',
        'suggested_fix': 'Join each checked result to the validated ledger entry by id and take anchor.path; apply in both report() and demo().',
        'boundary': 'Original line sources are protected and remain unchanged.'}]}
    Path('gathering/citation-report-probe-36.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
