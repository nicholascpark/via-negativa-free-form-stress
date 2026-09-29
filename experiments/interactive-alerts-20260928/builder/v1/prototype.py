"""v1: independent duct episodes; source-order branch remains provisional."""
import json
from pathlib import Path


def decisions(events, use_source_order=False):
    states = {}
    result = []
    for event in events:
        key = (event['cabinet'], event['port'])
        state = states.setdefault(key, {'active': False, 'last_n': None})
        page, reason = False, 'unreadable_preserves_episode'
        n = event['n']
        if use_source_order and state['last_n'] is not None and n <= state['last_n']:
            reason = 'non_newer_source_row'
        else:
            state['last_n'] = n
            if event['reading'] == 'NORMAL':
                state['active'] = False
                reason = 'normal_rearms'
            elif event['reading'] == 'HIGH':
                page = not state['active']
                reason = 'episode_onset' if page else 'ongoing_episode'
                state['active'] = True
        result.append({'id': event['id'], 'page': page, 'reason': reason,
                       'active_after': state['active'], 'last_n_after': state['last_n']})
    return result


def page_ids(events, use_source_order=False):
    return [d['id'] for d in decisions(events, use_source_order) if d['page']]


if __name__ == '__main__':
    streams = json.loads(Path(__file__).with_name('streams.json').read_text())
    for name, events in streams.items():
        print(json.dumps({'capture': name, 'delivery_episode': page_ids(events),
                          'provisional_source_episode': page_ids(events, True)}))
