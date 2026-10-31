import os, sys, unittest, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import inventory, triage

ROOT = os.path.join(os.path.dirname(__file__), "..", "fixtures", "drive")
NOW = time.mktime(time.strptime("2026-08-24", "%Y-%m-%d"))

# git does not store mtimes, so a fresh clone stamps every fixture "today".
# Pin them here: the two stale fixtures well over a year before NOW, the rest near NOW.
STALE = {os.path.join("Principal", "Research", "market_sizing.md"),
         os.path.join("Shared", "Inbox", "IMG_4471.md")}

def setUpModule():
    for dirpath, _, names in os.walk(ROOT):
        for n in names:
            p = os.path.join(dirpath, n)
            t = NOW - (400 if os.path.relpath(p, ROOT) in STALE else 1) * 86400
            os.utime(p, (t, t))

def go():
    files = inventory.walk(ROOT)
    return files, triage.run(files, now=NOW)

def of(pairs, verdict):
    return [p for p in pairs if p.verdict == verdict]

class EachKindIsSeparated(unittest.TestCase):
    def test_identical_bytes_are_the_only_auto_case(self):
        _, (pairs, _, _) = go()
        auto, human = triage.plan(pairs)
        self.assertEqual(len(auto), 1)
        self.assertEqual(auto[0].verdict, triage.IDENTICAL)
        for p in human:
            self.assertNotEqual(p.verdict, triage.IDENTICAL)

    def test_same_name_different_content_is_split_brain(self):
        _, (pairs, _, _) = go()
        sb = of(pairs, triage.SPLIT_BRAIN)
        self.assertEqual(len(sb), 1)
        self.assertIn("budget_2026", sb[0].a.rel)
        self.assertIn("budget_2026", sb[0].b.rel)

    def test_split_brain_is_never_auto_merged(self):
        _, (pairs, _, _) = go()
        auto, _ = triage.plan(pairs)
        self.assertFalse([p for p in auto if p.verdict == triage.SPLIT_BRAIN])

    def test_complementary_reports_what_each_side_uniquely_holds(self):
        _, (pairs, _, _) = go()
        c = of(pairs, triage.COMPLEMENT)[0]
        self.assertTrue(c.unique_to_a)
        self.assertTrue(c.unique_to_b)

    def test_near_duplicate_is_a_superset_not_a_conflict(self):
        _, (pairs, _, _) = go()
        n = of(pairs, triage.NEAR)[0]
        self.assertTrue(bool(n.unique_to_a) != bool(n.unique_to_b))

class ItDoesNotOverreach(unittest.TestCase):
    def test_unrelated_files_produce_no_pair(self):
        _, (pairs, _, _) = go()
        rels = {p.a.rel for p in pairs} | {p.b.rel for p in pairs}
        self.assertNotIn(os.path.join("Shared", "Projects", "ops_weekly.md"), rels)

    def test_stale_and_empty_are_reported_not_actioned(self):
        _, (pairs, stale, empty) = go()
        self.assertEqual(len(stale), 2)
        self.assertEqual(len(empty), 1)
        auto, _ = triage.plan(pairs)
        for p in auto:
            self.assertEqual(p.verdict, triage.IDENTICAL)

class ItNeverDeletes(unittest.TestCase):
    """The property that matters most on someone else's private drive."""
    def test_no_module_calls_a_destructive_function(self):
        src = os.path.join(os.path.dirname(__file__), "..", "src")
        banned = ("os.remove", "os.unlink", "shutil.rmtree", "os.rmdir", "send2trash")
        for name in os.listdir(src):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(src, name), encoding="utf-8") as fh:
                body = fh.read()
            for b in banned:
                self.assertNotIn(b, body, f"{name} references {b}")

    def test_auto_set_contains_only_identical(self):
        self.assertEqual(triage.AUTO, {triage.IDENTICAL})

if __name__ == "__main__":
    unittest.main()
