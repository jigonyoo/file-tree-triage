# file-tree-triage

Deduplication for a real person's drive, where the tool's job is to be **clear about which pairs it
is not allowed to decide**. It produces a plan. It never deletes anything.

```
make demo    # triages the fixture drive
make test    # 9 tests
```

## The measured run

12 files, 66 possible pairs, **4 related pairs**:

| verdict | count | may act unattended? |
|---|---:|---|
| `IDENTICAL` | 1 | **yes** — byte-for-byte |
| `NEAR` | 1 | no |
| `COMPLEMENTARY` | 1 | no |
| `SPLIT_BRAIN` | 1 | no |

**1 pair is safe to collapse. 3 go to a person.** Plus 2 stale files (untouched over a year) and
1 empty file, reported and left alone.

**Deletes in the plan: 0.**

## The four kinds, and why they are not one kind

**IDENTICAL** — `Principal/Research/market_sizing.md` and `Shared/Research/market_sizing.md` are
the same bytes. This is the only verdict allowed to act without asking.

**SPLIT_BRAIN** — two files called `budget_2026.md`, one saying headcount 12 / opex 480k, the other
14 / 512k with a note about the board. Same name, different content. Merging them invents a budget
that never existed and nothing downstream will ever say so. Held, never merged.

**COMPLEMENTARY** — `vendors.md` has a contact address; `vendors_v2.md` has a third vendor and
pricing notes. Each holds something the other lacks, so there is no winner to pick — the merged
version has to be *built*, and that is the owner's decision, not the tool's.

**NEAR** — `onboarding.md` and `onboarding_FINAL.md` differ by one line. One contains the other.
Still not automatic: "FINAL" in a filename is a claim, not evidence.

## The property that matters on a private drive

A test reads every module in `src/` and asserts that none of them references `os.remove`,
`os.unlink`, `shutil.rmtree`, `os.rmdir` or `send2trash`. Another asserts the auto-action set
contains exactly one verdict. Those are machine checks on the promise, not a sentence in a README
saying we are careful.

The output is a staging plan: each move records the original path so any step can be reversed. A
confident wrong classification is cheap — you move the file back. A confident wrong delete is not.
That asymmetry, not confidence, is what decides where the human boundary sits.

## Honest limits

- Comparison is line-set overlap on text. Binary files, images and PDFs hash-match or nothing;
  there is no perceptual or semantic similarity here.
- No Google Drive API. It walks a local directory. Drive adds shortcuts, shared drives, revision
  history and two files legitimately having one name — all of which change the problem.
- "Stale" is mtime over a threshold. On a synced drive mtime lies more often than it tells the truth.
- The fixture is synthetic and 12 files. The ratios above describe the fixture, not your drive.
- It suggests. It does not tidy. Someone still has to decide the three.

## Layout

```
fixtures/drive/   12 files across two territories, one of each duplicate pattern
src/inventory.py  walk once, hash, read lines, never write
src/triage.py     classify every pair; AUTO = {IDENTICAL} and nothing else
src/cli.py        summary to stdout, full plan to out/plan.md
tests/            9 tests, two of which assert the tool cannot delete
```
