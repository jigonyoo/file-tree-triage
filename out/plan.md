# File triage plan

12 files. **Nothing in this plan deletes anything.** Every action is a move into a staging folder with the original path recorded, so any step can be undone.

## Safe to collapse without asking (1)

- `Principal/Research/market_sizing.md` and `Shared/Research/market_sizing.md` — identical bytes (`sha 4cf9459800c6`)

## Needs a person (3)

### 1. SPLIT_BRAIN
- `Principal/Admin/budget_2026.md`
- `Shared/Projects/budget_2026.md`
- **Why:** same filename, different content - merging them invents a file that never existed
- Only in the first: 'Headcount 12', 'Opex 480k'
- Only in the second: 'Headcount 14', 'Note: revised after board', 'Opex 512k'

### 2. COMPLEMENTARY
- `Principal/Research/vendors.md`
- `Shared/Research/vendors_v2.md`
- **Why:** each file holds a line the other lacks - this cannot be resolved by choosing a winner, the merged version has to be built
- Only in the first: 'Contact: acme@example.com'
- Only in the second: '- Cygnus', 'Pricing notes attached'

### 3. NEAR
- `Shared/Projects/onboarding.md`
- `Shared/Projects/onboarding_FINAL.md`
- **Why:** one is contained in the other
- Only in the second: '4 badge'

## Stale — untouched over a year (2)

- `Principal/Research/market_sizing.md`
- `Shared/Inbox/IMG_4471.md`

## Empty (1)

- `Shared/Inbox/untitled.md`