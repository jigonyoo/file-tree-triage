"""Classify every pair. The output is a plan, never an action."""
from dataclasses import dataclass
from itertools import combinations

IDENTICAL   = "IDENTICAL"      # byte-for-byte: safe to collapse
NEAR        = "NEAR"           # one is a superset/subset in content
COMPLEMENT  = "COMPLEMENTARY"  # each holds something the other lacks
SPLIT_BRAIN = "SPLIT_BRAIN"    # same name, different content
DISTINCT    = "DISTINCT"

AUTO = {IDENTICAL}             # the only verdict allowed to act without a person

@dataclass
class Pair:
    a: object
    b: object
    verdict: str
    why: str
    unique_to_a: tuple = ()
    unique_to_b: tuple = ()

def _name(f):
    import os
    return os.path.basename(f.rel).lower()

def classify(a, b):
    if a.sha == b.sha:
        return Pair(a, b, IDENTICAL, "identical bytes")
    sa, sb = set(a.lines), set(b.lines)
    if not sa and not sb:
        return Pair(a, b, DISTINCT, "both empty")
    only_a, only_b = tuple(sorted(sa - sb)), tuple(sorted(sb - sa))
    shared = sa & sb
    if _name(a) == _name(b):
        return Pair(a, b, SPLIT_BRAIN,
                    "same filename, different content - merging them invents a file that never existed",
                    only_a, only_b)
    if not shared:
        return Pair(a, b, DISTINCT, "no shared content")
    overlap = len(shared) / max(len(sa), len(sb))
    if overlap < 0.5:
        return Pair(a, b, DISTINCT, f"only {overlap:.0%} shared")
    if only_a and only_b:
        return Pair(a, b, COMPLEMENT,
                    "each file holds a line the other lacks - this cannot be resolved by "
                    "choosing a winner, the merged version has to be built",
                    only_a, only_b)
    return Pair(a, b, NEAR,
                "one is contained in the other" if not only_a else "one is contained in the other",
                only_a, only_b)

def run(files, stale_days=365, now=None):
    import time
    now = now or time.time()
    pairs = [classify(a, b) for a, b in combinations(files, 2)]
    pairs = [p for p in pairs if p.verdict != DISTINCT]
    stale = [f for f in files if (now - f.mtime) / 86400 > stale_days]
    empty = [f for f in files if f.size == 0]
    return pairs, stale, empty

def plan(pairs):
    """What may run unattended, and what may not."""
    auto = [p for p in pairs if p.verdict in AUTO]
    human = [p for p in pairs if p.verdict not in AUTO]
    return auto, human
