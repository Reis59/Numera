# NUMERA changelog

## Build 0.2.1 — Distinct examples and exercises
- Replaced the repeated `18 − 2 × 5` practice question with a different order-of-operations problem.
- Added a regression test to prevent the lesson example from being reused as its exercise.

## Build 0.2 — Enhanced learning journey
- Replaced the single fixed question per lesson with a randomized two-question selection from a minimum three-question topic pool.
- Added 32 lesson units and 141 original practice questions across four worlds.
- Added sound effects generated with Web Audio and a persistent mute setting.
- Added daily quest rewards with server-side once-per-day protection.
- Added streak tracking, achievements, coins, and four final-boss challenges.
- Added 32 flashcards with spaced-review scheduling and due-card prioritization.
- Added topic-level weak-area recommendations to statistics.
- Added timed practice simulation, expanded interactive math lab, and local admin overview.
- Added API integration tests and curriculum validation tests.

## Build 0.1 — Initial local MVP
- Four learning worlds, basic learning path, lesson viewer, question cards, math lab, practice simulator, SQLite progress.

## Build 0.2.2 — NUMI Personality & Accessory Shop
- Made NUMI feel more alive with gentle idle movement, blinking eyes, hover reactions, and happy/sad expressions.
- Added an accessory shop with eight cosmetic items: explorer cap, champion crown, smart glasses, star halo, cheerful bow, scarf, alien antenna, and lucky flower.
- XP earned from learning can now be spent on accessories; coins remain a separate collectible balance.
- Added persistent owned-item inventory and equipped accessory storage in SQLite.
- Added server-side validation for item IDs, XP balance, duplicate purchases, and ownership before equipping.
- Added forward-compatible database tables; existing progress, XP, and coins are preserved.
- Added shop API regression tests.

## Build 0.2.3 — Accessory visibility fix
- Fixed NUMI's accessory layer being clipped by the mascot container's overflow setting.
- Added accessory-specific placement for hats, crowns, glasses, halo, bow, scarf, antenna, and flower.
- Applied the equipped accessory class to every NUMI mascot instance, including lesson and reward screens.
- Added cache-busting asset versions and a regression test for accessory rendering.


## Build 0.2.4 — First positioning correction
- Attempted to anchor the original accessory overlay to the mascot. This did not resolve the rendering issue on the user's installation.
- Bumped static asset cache versions.

## Build 0.2.6 — NUMI cartoon illustration redesign
- Replaced CSS mascot shapes and emoji overlays with nine complete transparent PNG character illustrations.
- Added a plain NUMI plus eight integrated looks: cap, crown, glasses, halo, bow, scarf, antenna, and flower.
- The shop previews the actual illustrated characters; equipping an item switches the entire character image.
- Sidebar, hero, lesson result, and shop preview use the same image-selection logic.
- Added automated checks for all illustration files, transparency, dimensions, image mapping, and responsive display.
