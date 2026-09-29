"""Independent audit runner. Expectations were frozen before final candidate.

Run from any directory with Python 3.10+; all writes stay beneath audit/.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'audit'
SOURCE = ROOT / 'relay' / 'candidate-frozen' / 'v3'
CANDIDATE = AUDIT / 'frozen-candidate'
FROZEN = ROOT / 'relay' / 'setup-frozen'


def read_json(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    provenance = []
    manifests = [
        (ROOT / 'setup-manifest.json', FROZEN),
        (ROOT / 'relay' / 'candidate-frozen.json', SOURCE.parent),
        (AUDIT / 'holdout-manifest.json', ROOT),
    ]
    manifests += [(ROOT / 'relay' / f'question-{i:02}.json',
                   ROOT / 'relay' / f'question-{i:02}-before-answer')
                  for i in range(1, 4)]
    for manifest, base in manifests:
        for name, expected in read_json(manifest)['hashes'].items():
            actual = digest(base / name)
            provenance.append({'manifest': str(manifest.relative_to(ROOT)),
                               'file': name, 'pass': actual == expected})
    if not all(item['pass'] for item in provenance):
        raise RuntimeError('Frozen artifact checksum mismatch')
    if not CANDIDATE.exists():
        shutil.copytree(SOURCE, CANDIDATE)
    for source_path in SOURCE.iterdir():
        if source_path.is_file():
            assert digest(source_path) == digest(CANDIDATE / source_path.name)
    sys.path.insert(0, str(CANDIDATE))
    notifier = load_module('audited_notifier', CANDIDATE / 'notifier.py')
    baseline = load_module('audited_baseline', FROZEN / 'public' / 'baseline.py')

    public = read_json(FROZEN / 'public' / 'streams.json')
    # Explicit expected arrays are stated in the pre-existing frozen dossier.
    expected_public = {
        'long_spell': ['long-2'], 'quick_return': ['quick-2', 'quick-4'],
        'two_ports': ['ports-3', 'ports-4'], 'reconnected': ['reconnect-2'],
        'unreadable_patch': ['invalid-2'], 'quiet': [],
        'already_high': ['startup-1'], 'two_cabinets': ['cabs-3', 'cabs-4'],
    }
    cases = [dict(group='public', name=name, events=events,
                  expected_page_ids=expected_public[name])
             for name, events in public.items()]
    cases += [dict(case, group='private_user')
              for case in read_json(FROZEN / 'user-private' / 'cases.json')]
    cases += [dict(case, group='auditor_holdout')
              for case in read_json(AUDIT / 'holdouts.json')]

    case_results, metamorphic, interface, baseline_results = [], [], [], []
    for case in cases:
        events, expected = case['events'], case['expected_page_ids']
        identity = {'group': case['group'], 'case': case['name']}
        actual = notifier.page_ids(copy.deepcopy(events))
        case_results.append(dict(identity, expected=expected, actual=actual,
                                 passed=actual == expected))
        for cooldown in (20, 60):
            actual_old = baseline.page_ids(events, cooldown=cooldown)
            baseline_results.append(dict(identity, cooldown=cooldown,
                                         actual=actual_old, expected=expected,
                                         passed=actual_old == expected,
                                         extra=[x for x in actual_old if x not in expected],
                                         missed=[x for x in expected if x not in actual_old]))
        sources = sorted({(e['cabinet'], e['port']) for e in events})
        offsets = {source: 100000 * (index + 1)
                   for index, source in enumerate(sources)}
        variants = {
            'compact_receipt_times': [dict(e, t=i) for i, e in enumerate(events)],
            'stretched_receipt_times': [dict(e, t=100 + i * 1000000)
                                        for i, e in enumerate(events)],
            'source_affine_counters': [dict(e, n=10 * e['n'] + offsets[(e['cabinet'], e['port'])])
                                       for e in events],
            'source_label_swap': [dict(e, cabinet={'A': 'B', 'B': 'A'}[e['cabinet']],
                                      port={'left': 'right', 'right': 'left'}[e['port']])
                                  for e in events],
        }
        for transformation, transformed in variants.items():
            actual_variant = notifier.page_ids(transformed)
            metamorphic.append(dict(identity, transformation=transformation,
                                    expected=expected, actual=actual_variant,
                                    passed=actual_variant == expected))
        decisions = notifier.decisions(copy.deepcopy(events))
        incremental = notifier.Notifier()
        incremental_rows = [incremental.process(copy.deepcopy(e)) for e in events]
        interface.append(dict(
            identity,
            repeated_batch_passed=notifier.page_ids(copy.deepcopy(events)) == expected,
            trace_passed=([row['id'] for row in decisions if row['page']] == expected
                          and len(decisions) == len(events)
                          and all(all(row[k] == value for k, value in event.items())
                                  for event, row in zip(events, decisions))),
            incremental_passed=incremental_rows == decisions))
    empty_passed = notifier.page_ids([]) == [] and notifier.decisions([]) == []

    # Reproduce claims from the frozen candidate; these remain worker tests.
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    worker = subprocess.run([sys.executable, str(CANDIDATE / 'test_notifier.py')],
                            cwd=AUDIT, env=env, capture_output=True, text=True)
    (AUDIT / 'worker-test-rerun.txt').write_text(worker.stdout + worker.stderr)
    cli = {}
    outputs = {}
    for fmt in ('table', 'json', 'csv'):
        command = [sys.executable, str(CANDIDATE / 'notifier.py'), '--format', fmt]
        result = subprocess.run(command, cwd=AUDIT, env=env, capture_output=True, text=True)
        (AUDIT / f'cli-output.{"txt" if fmt == "table" else fmt}').write_text(result.stdout)
        outputs[fmt] = result.stdout
        cli[fmt] = {'exit_code': result.returncode, 'stderr': result.stderr}
    report = json.loads(outputs['json'])
    saved_report = read_json(SOURCE / 'comparison.json')
    csv_rows = list(csv.DictReader(io.StringIO(outputs['csv'])))
    saved_csv = list(csv.DictReader(io.StringIO((SOURCE / 'records.csv').read_text())))
    claims = {
        'saved_json_reproduced': report == saved_report,
        'saved_csv_reproduced': csv_rows == saved_csv,
        'all_public_records_shown': len(report['records']) == sum(map(len, public.values())),
        'summary_counts': {key: sum(len(row[key]) for row in report['summary'])
                           for key in ('cooldown20', 'cooldown60', 'candidate')},
        'cli_all_succeeded': all(v['exit_code'] == 0 for v in cli.values()),
    }

    timeline = []
    for index in range(1, 4):
        question = read_json(ROOT / 'relay' / f'question-{index:02}.json')
        answer = read_json(ROOT / 'relay' / f'answer-{index:02}.json')
        timeline.append({
            'round': index, 'question_words': len(question['text'].split()),
            'answer_words': len(answer['text'].split()),
            'reply_latency_seconds': (datetime.fromisoformat(answer['at_utc']) -
                                      datetime.fromisoformat(question['at_utc'])).total_seconds(),
        })
    setup_at = read_json(ROOT / 'setup-manifest.json')['at_utc']
    candidate_at = read_json(ROOT / 'relay' / 'candidate-frozen.json')['at_utc']
    cost = {'question_rounds': 3, 'timeline': timeline,
            'setup_to_candidate_seconds': (datetime.fromisoformat(candidate_at) -
                                           datetime.fromisoformat(setup_at)).total_seconds(),
            'tokens_money_compute': 'Not measured; wall time includes coordination and agent work.'}

    result = {'at_utc': datetime.now(timezone.utc).isoformat(),
              'source': 'relay/candidate-frozen/v3',
              'adaptation': 'None; direct documented page_ids/decisions/Notifier interfaces.',
              'provenance': provenance, 'cases': case_results,
              'metamorphic_checks': metamorphic, 'interface_checks': interface,
              'empty_capture_passed': empty_passed,
              'baseline_comparisons': baseline_results,
              'worker_tests': {'exit_code': worker.returncode, 'log': 'worker-test-rerun.txt'},
              'cli': cli, 'claim_checks': claims, 'rough_cost': cost}
    (AUDIT / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    groups = {group: {'passed': sum(c['passed'] for c in case_results if c['group'] == group),
                      'total': sum(c['group'] == group for c in case_results)}
              for group in ('public', 'private_user', 'auditor_holdout')}
    passed = (all(c['passed'] for c in case_results + metamorphic)
              and all(all(c[k] for k in ('repeated_batch_passed', 'trace_passed', 'incremental_passed'))
                      for c in interface)
              and empty_passed and worker.returncode == 0
              and all(claims[k] for k in ('saved_json_reproduced', 'saved_csv_reproduced',
                                        'all_public_records_shown', 'cli_all_succeeded')))
    print(json.dumps({'groups': groups, 'metamorphic_passed': sum(c['passed'] for c in metamorphic),
                      'metamorphic_total': len(metamorphic), 'provenance_checks': len(provenance),
                      'claim_checks': claims, 'rough_cost': cost, 'all_passed': passed}, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
