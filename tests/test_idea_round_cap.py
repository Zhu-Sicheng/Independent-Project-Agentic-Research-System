"""Per-idea optimisation round cap."""

import unittest

from factorlab.xy_pipeline import filter_capped_ideas


def _candidate(idea_id: str, expression: str = "rank(close)") -> dict:
    return {"idea_id": idea_id, "expression": expression}


class TestIdeaRoundCap(unittest.TestCase):
    def test_keeps_ideas_under_the_cap(self):
        rounds = {"idea_a": 2, "idea_b": 0}
        kept, dropped = filter_capped_ideas(
            [_candidate("idea_a"), _candidate("idea_b")], rounds, 3
        )
        self.assertEqual([c["idea_id"] for c in kept], ["idea_a", "idea_b"])
        self.assertEqual(dropped, 0)

    def test_drops_ideas_at_the_cap(self):
        rounds = {"idea_a": 3, "idea_b": 1}
        kept, dropped = filter_capped_ideas(
            [_candidate("idea_a"), _candidate("idea_b")], rounds, 3
        )
        self.assertEqual([c["idea_id"] for c in kept], ["idea_b"])
        self.assertEqual(dropped, 1)

    def test_zero_disables_the_cap(self):
        rounds = {"idea_a": 99}
        kept, dropped = filter_capped_ideas([_candidate("idea_a")], rounds, 0)
        self.assertEqual(len(kept), 1)
        self.assertEqual(dropped, 0)

    def test_candidates_without_idea_id_are_kept(self):
        kept, dropped = filter_capped_ideas(
            [{"expression": "rank(close)"}], {"idea_a": 5}, 3
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(dropped, 0)

    def test_rounds_are_counted_once_per_round(self):
        rounds = {"idea_a": 2}
        # second submission in the same round is still one consumed round when
        # the caller increments after the filter
        kept, _ = filter_capped_ideas([_candidate("idea_a")], rounds, 3)
        self.assertEqual(len(kept), 1)
        rounds["idea_a"] += 1
        kept, dropped = filter_capped_ideas([_candidate("idea_a")], rounds, 3)
        self.assertEqual(kept, [])
        self.assertEqual(dropped, 1)


if __name__ == "__main__":
    unittest.main()
