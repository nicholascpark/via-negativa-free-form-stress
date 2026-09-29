"""The current notifier, reduced to pure Python and printable page IDs."""
import json
from pathlib import Path


def page_ids(events, cooldown=20):
    last_page = {}
    pages = []
    for event in events:
        cabinet = event['cabinet']
        if event['reading'] == 'HIGH' and event['t'] - last_page.get(cabinet, float('-inf')) >= cooldown:
            pages.append(event['id'])
            last_page[cabinet] = event['t']
    return pages


if __name__ == '__main__':
    streams = json.loads(Path(__file__).with_name('streams.json').read_text())
    for name, events in streams.items():
        print(name, page_ids(events))
