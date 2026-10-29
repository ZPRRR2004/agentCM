"""Event boundaries and length estimates used by execution and preview."""
from pathlib import Path
import tempfile
import unittest

from src.split.main import load_config
from src.split.splitter import split_trajectory, window_ranges
from src.split.token_counter import count_core_tokens, range_token_counter


class EventSplittingTests(unittest.TestCase):
    def test_text_size_does_not_change_boundaries_or_truncate_events(self):
        events = [{'event_id':str(i), 'thought':'x' * (200000 if i == 1 else 3)} for i in range(5)]
        windows = split_trajectory(events, {'max_window_events':2, 'overlap_events':1})
        self.assertEqual([[e['event_id'] for e in w['core_events']] for w in windows], [['0','1'],['2','3'],['4']])
        self.assertEqual([[e['event_id'] for e in w['overlap_events']] for w in windows], [[],['1'],['3']])
        self.assertEqual([e for w in windows for e in w['core_events']], events)
        self.assertGreater(windows[0]['metadata']['core_tokens'], 40000)
        self.assertNotIn('oversized', windows[0]['metadata'])

    def test_overlap_can_span_prior_windows_and_stops_at_trajectory_start(self):
        self.assertEqual(list(window_ranges(5, {'max_window_events':2, 'overlap_events':4})),
                         [(0,0,2),(0,2,4),(0,4,5)])
        self.assertEqual(split_trajectory([], {'max_window_events':2,'overlap_events':0}), [])
        for key, bad in [('max_window_events',0),('max_window_events',True),('overlap_events',-1)]:
            with self.assertRaises(ValueError):
                list(window_ranges(5, {'max_window_events':2,'overlap_events':0,key:bad}))

    def test_prefix_estimate_equals_full_serialization_for_all_slices(self):
        events = [{'event_id':str(i),'text':text} for i,text in enumerate(['中文🙂', 'a\n\"b', '\\ \t', 'x'*10000])]
        counter = range_token_counter(events)
        for start in range(len(events)+1):
            for end in range(start,len(events)+1):
                self.assertEqual(counter(start,end),count_core_tokens(events[start:end]))

    def test_cli_has_four_parameters_and_rejects_removed_token_limit(self):
        default = Path(__file__).resolve().parents[1] / 'src/split/config.yaml'
        config = load_config(default)
        self.assertEqual(set(config), {'max_window_events','overlap_events','max_previous_summary_tokens','max_future_summary_tokens'})
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'config.yaml'
            path.write_text(default.read_text()+'\nmax_window_tokens: 6000\n')
            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == '__main__':
    unittest.main()
