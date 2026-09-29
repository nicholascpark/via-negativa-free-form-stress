"""Exploratory alternatives, not a bench contract. Python standard library only."""
import json
from pathlib import Path
from baseline import page_ids


def episode_pages(events, scope):
    """Provisional: one page until NORMAL; INVALID leaves state unchanged."""
    active, pages = set(), []
    for e in events:
        key = e['cabinet'] if scope == 'cabinet' else (e['cabinet'], e['port'])
        if e['reading'] == 'NORMAL':
            active.discard(key)
        elif e['reading'] == 'HIGH' and key not in active:
            active.add(key)
            pages.append(e['id'])
    return pages


if __name__ == '__main__':
    streams = json.loads(Path(__file__).with_name('streams.json').read_text())
    for name, events in streams.items():
        print(json.dumps({'capture': name, 'cooldown20': page_ids(events),
                          'cooldown60': page_ids(events, 60),
                          'episode_cabinet': episode_pages(events, 'cabinet'),
                          'episode_port': episode_pages(events, 'port')}))
