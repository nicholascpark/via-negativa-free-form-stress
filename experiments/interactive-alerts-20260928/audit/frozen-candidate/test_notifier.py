"""Synthetic development checks; expected behavior comes from technician answers."""
import itertools
import json
from pathlib import Path
import unittest

from notifier import Notifier, decisions, page_ids


def event(label, n, reading, cabinet='A', port='left', t=0):
    return dict(id=label, t=t, cabinet=cabinet, port=port, n=n, reading=reading)


class NotifierTests(unittest.TestCase):
    def test_public_capture_regressions(self):
        # All public captures were exposed during development, not a held-out test.
        expected = {'long_spell': ['long-2'], 'quick_return': ['quick-2', 'quick-4'],
                    'two_ports': ['ports-3', 'ports-4'], 'reconnected': ['reconnect-2'],
                    'unreadable_patch': ['invalid-2'], 'quiet': [],
                    'already_high': ['startup-1'], 'two_cabinets': ['cabs-3', 'cabs-4']}
        streams = json.loads(Path(__file__).with_name('streams.json').read_text())
        for name, events in streams.items():
            with self.subTest(capture=name):
                self.assertEqual(page_ids(events), expected[name])

    def test_stale_normal_does_not_rearm(self):
        rows = [event('a', 2, 'HIGH'), event('b', 1, 'NORMAL'), event('c', 3, 'HIGH')]
        self.assertEqual(page_ids(rows), ['a'])
        self.assertFalse(decisions(rows)[1]['fresh'])

    def test_invalid_advances_frontier_and_does_not_clear(self):
        rows = [event('a', 1, 'HIGH'), event('b', 3, 'INVALID'),
                event('c', 2, 'NORMAL'), event('d', 4, 'HIGH')]
        self.assertEqual(page_ids(rows), ['a'])
        self.assertEqual(decisions(rows)[1]['newest_n_after'], 3)
        self.assertEqual(decisions(rows)[2]['reason'], 'ignored_non_newer')

    def test_invalid_before_first_high_does_not_arm_requirement(self):
        self.assertEqual(page_ids([event('a', 2, 'INVALID'), event('b', 3, 'HIGH')]), ['b'])
        self.assertEqual(page_ids([event('a', 2, 'INVALID'), event('b', 1, 'HIGH')]), [])

    def test_one_duct_cannot_clear_another(self):
        rows = [event('a', 1, 'HIGH'), event('b', 500, 'NORMAL', port='right'),
                event('c', 2, 'HIGH'), event('d', 501, 'HIGH', port='right'),
                event('e', 1, 'HIGH', cabinet='B')]
        self.assertEqual(page_ids(rows), ['a', 'd', 'e'])

    def test_equal_counter_retry_ignored(self):
        rows = [event('a', 1, 'HIGH'), event('retry', 1, 'HIGH', t=1000)]
        self.assertEqual(page_ids(rows), ['a'])
        self.assertEqual(decisions(rows)[1]['reason'], 'ignored_non_newer')

    def test_fresh_recovery_immediately_rearms(self):
        # Equal receipt times deliberately rule out a hidden cooldown.
        rows = [event('a', 1, 'HIGH'), event('b', 2, 'NORMAL'), event('c', 3, 'HIGH')]
        self.assertEqual(page_ids(rows), ['a', 'c'])

    def test_no_reminder_after_long_silence(self):
        self.assertEqual(page_ids([event('a', 1, 'HIGH'),
                                   event('b', 2, 'HIGH', t=10**9)]), ['a'])

    def test_no_memory_crosses_captures(self):
        first = event('a', 1, 'HIGH')
        later = event('b', 2, 'HIGH')
        continuous = Notifier()
        self.assertTrue(continuous.process(first)['page'])
        self.assertFalse(continuous.process(later)['page'])
        self.assertEqual(page_ids([later]), ['b'])

    def test_generated_retry_and_time_invariance(self):
        # 3^5=243 source histories. A retry and receipt-time stretch cannot change
        # pages under confirmed current-condition / no-reminder requirements.
        for readings in itertools.product(('HIGH', 'NORMAL', 'INVALID'), repeat=5):
            rows = [event(str(i), i, reading, t=i) for i, reading in enumerate(readings)]
            with self.subTest(readings=readings):
                expected = page_ids(rows)
                augmented = []
                for row in rows:
                    augmented += [row, dict(row, id='retry-' + row['id'], t=row['t'] + 1)]
                self.assertEqual(page_ids(augmented), expected)
                self.assertEqual(page_ids([dict(row, t=row['t'] * 1000000)
                                           for row in rows]), expected)

    def test_incremental_interface_matches_batch(self):
        rows = [event('a', 3, 'HIGH'), event('b', 4, 'NORMAL'), event('c', 5, 'HIGH')]
        notifier = Notifier()
        self.assertEqual([notifier.process(row) for row in rows], decisions(rows))


if __name__ == '__main__':
    unittest.main(verbosity=2)
