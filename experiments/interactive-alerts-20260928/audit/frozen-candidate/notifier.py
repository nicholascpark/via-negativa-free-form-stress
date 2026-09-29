"""Offline current-condition notifier for the confirmed synthetic bench contract."""
import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from baseline import page_ids as cooldown_page_ids


@dataclass
class DuctState:
    newest_n: int | None = None
    active: bool = False


class Notifier:
    """Keep one instance across a capture; create a new one for each capture."""

    def __init__(self):
        self.ducts = {}

    def process(self, event):
        reading = event['reading']
        if reading not in {'HIGH', 'NORMAL', 'INVALID'}:
            raise ValueError(f"Unsupported reading: {reading!r}")
        n = event['n']
        if type(n) is not int:
            raise ValueError('n must be an integer')
        key = (event['cabinet'], event['port'])
        state = self.ducts.setdefault(key, DuctState())
        fresh = state.newest_n is None or n > state.newest_n
        page = False
        active_before = state.active
        if not fresh:
            reason = 'ignored_non_newer'
        else:
            # Even INVALID is newer source evidence; admission precedes interpretation.
            state.newest_n = n
            if reading == 'HIGH':
                page = not state.active
                state.active = True
                reason = 'new_problem' if page else 'continuing_problem'
            elif reading == 'NORMAL':
                state.active = False
                reason = 'recovered' if active_before else 'normal'
            else:
                reason = 'unreadable_preserves_episode'
        return dict(event, fresh=fresh, page=page, reason=reason,
                    active_before=active_before, active_after=state.active,
                    newest_n_after=state.newest_n)


def decisions(events):
    """Process delivery order, starting with no memory; return one decision per row."""
    notifier = Notifier()
    return [notifier.process(event) for event in events]


def page_ids(events):
    return [row['id'] for row in decisions(events) if row['page']]


def compare(streams):
    """Each named capture starts afresh under all three policies."""
    summaries, records = [], []
    for name, events in streams.items():
        old20 = cooldown_page_ids(events)
        old60 = cooldown_page_ids(events, cooldown=60)
        trace = decisions(events)
        summaries.append({'capture': name, 'cooldown20': old20, 'cooldown60': old60,
                          'candidate': [row['id'] for row in trace if row['page']]})
        old20_set, old60_set = set(old20), set(old60)
        records.extend(dict(row, capture=name, cooldown20_page=row['id'] in old20_set,
                            cooldown60_page=row['id'] in old60_set) for row in trace)
    return {'summary': summaries, 'records': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path,
                        default=Path(__file__).with_name('streams.json'))
    parser.add_argument('--format', choices=('table', 'json', 'csv'), default='table')
    args = parser.parse_args()
    report = compare(json.loads(args.input.read_text()))
    if args.format == 'json':
        print(json.dumps(report, indent=2))
    elif args.format == 'csv':
        fields = ['capture', 'id', 't', 'cabinet', 'port', 'n', 'reading',
                  'cooldown20_page', 'cooldown60_page', 'page', 'fresh', 'reason',
                  'active_before', 'active_after', 'newest_n_after']
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(report['records'])
    else:
        print('capture | current 20s | proposed 60s | episode candidate')
        for row in report['summary']:
            values = [row['capture']] + [', '.join(row[key]) or '—'
                                         for key in ('cooldown20', 'cooldown60', 'candidate')]
            print(' | '.join(values))


if __name__ == '__main__':
    main()
