import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import inventory, triage

def main():
    root = os.environ.get("ROOT", "fixtures/drive")
    out = os.environ.get("OUT", "out")
    os.makedirs(out, exist_ok=True)
    now = float(os.environ.get("NOW", time.time()))
    files = inventory.walk(root)
    pairs, stale, empty = triage.run(files, now=now)
    auto, human = triage.plan(pairs)

    counts = {}
    for p in pairs:
        counts[p.verdict] = counts.get(p.verdict, 0) + 1
    print(f"{len(files)} files, {len(files)*(len(files)-1)//2} possible pairs, "
          f"{len(pairs)} related pairs\n")
    for k in (triage.IDENTICAL, triage.NEAR, triage.COMPLEMENT, triage.SPLIT_BRAIN):
        print(f"  {k:<14} {counts.get(k,0)}")
    print(f"\n  auto-collapsible          {len(auto)}")
    print(f"  must go to a person       {len(human)}")
    print(f"  stale (untouched >1y)     {len(stale)}")
    print(f"  empty                     {len(empty)}")
    print(f"\n  deletes in this plan      0   (the plan never deletes; it stages and records an undo)")

    L = ["# File triage plan", "",
         f"{len(files)} files. **Nothing in this plan deletes anything.** Every action is a move "
         "into a staging folder with the original path recorded, so any step can be undone.", "",
         f"## Safe to collapse without asking ({len(auto)})", ""]
    for p in auto:
        L += [f"- `{p.a.rel}` and `{p.b.rel}` — {p.why} (`sha {p.a.sha[:12]}`)"]
    L += ["", f"## Needs a person ({len(human)})", ""]
    for i, p in enumerate(human, 1):
        L += [f"### {i}. {p.verdict}", f"- `{p.a.rel}`", f"- `{p.b.rel}`", f"- **Why:** {p.why}"]
        if p.unique_to_a:
            L.append(f"- Only in the first: {', '.join(repr(x) for x in p.unique_to_a)}")
        if p.unique_to_b:
            L.append(f"- Only in the second: {', '.join(repr(x) for x in p.unique_to_b)}")
        L.append("")
    L += [f"## Stale — untouched over a year ({len(stale)})", ""]
    L += [f"- `{f.rel}`" for f in stale]
    L += ["", f"## Empty ({len(empty)})", ""] + [f"- `{f.rel}`" for f in empty]
    with open(f"{out}/plan.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"\nwrote {out}/plan.md")

if __name__ == "__main__":
    main()
