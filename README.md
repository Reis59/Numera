# NUMERA — Build 0.2.6 (Enhanced MVP)

**Matematika Jadi Petualangan.** A local-first gamified mathematics learning app for SMP/MTs.

## Run on Windows 10/11
1. Extract the ZIP.
2. Install Python 3.10+ and make sure `python` is available in PATH.
3. Double-click `INSTALL.bat` (or `START.bat`, then open http://127.0.0.1:8000).
4. `STOP.bat` stops the local server.

No external AI API, Node.js, npm, or Python packages are required. The server uses Python's standard library and SQLite. Sound effects are synthesized in the browser using Web Audio (no audio files or external API).

## Demo profile
- Username: `demo` (local single-profile mode; no password)
- Database: `data/numera.db`
- The database persists progress, XP, coins, streak activity, answer history, flashcard review schedules, daily quest completion, and settings.

## Included in this build
- Four curriculum worlds and 32 lesson units, including explicit scientific notation, estimation, distributive factoring, arithmetic series, nets, and sphere volume topics.
- A bank of 141 questions (at least 4 per lesson); each lesson draws a randomized three-question subset and avoids repeating the exact previous set within the browser session.
- Lesson objectives, explanations, worked examples, recaps, immediate feedback, and level pass threshold.
- XP, coins, unlock progression, four final-boss challenges, daily streak tracking, once-per-day quest rewards, and achievement badges.
- 32 flashcards with ease-based spaced-review scheduling; due cards are prioritized in the review deck.
- Interactive topic map, math lab, dice experiment, and a timed NUMERA practice simulator.
- Sound effects for correct/wrong answers, navigation, level completion, and dice/reward interactions; sound toggle in header/settings.
- Student statistics with per-topic weak-area recommendations and a local admin overview.
- Responsive layout for desktop and mobile.

## Scope and honest limitations
This is an enhanced local MVP, not a production multi-user service. The admin screen is an overview, not a full CRUD content-management system. There is no real registration/login, secure multi-user authorization, class leaderboard, or cloud synchronization yet. The demo profile is not protected by authentication. Public leaderboard, class management, cloud sync, exports, a full question-authoring workflow, and comprehensive TKA-length content still need a later release. Some curriculum subtopics are combined into broader lessons; review the content with a mathematics teacher before formal exam preparation. All generated questions are labeled NUMERA practice, not official TKA questions.

The daily quest gives its bonus once per local calendar day. A streak increments on the first recorded learning activity of a new day. Sound starts only after browser interaction and can be disabled.

## Tests
From the project directory run:

```bat
python -m unittest discover -s tests -v
```

The tests validate curriculum structure, question answer-key bounds, uniqueness of options, flashcard coverage, NUMI illustration assets, image selection, and responsive display rules. They do not replace manual testing on the target Windows computer.

The automated suite also exercises the local HTTP API (progress rewards, no double XP, daily reward idempotency, flashcard review scheduling) and verifies migration from the previous Build 0.1 SQLite schema. The nine NUMI PNG variants (one plain plus eight accessories) are checked for file presence, transparency, and dimensions. A Chromium smoke test was attempted in the build environment but local navigation was blocked by its browser policy, so no browser-render pass is claimed. The backend purchase/equip flow is covered by automated API integration tests.

## Build 0.2.6 — NUMI and accessories
NUMI has been redesigned as a friendly, rounded cartoon mascot. Each look is a complete transparent PNG illustration: plain, cap, crown, glasses, halo, bow, scarf, antenna, and flower. The shop previews the finished character art, and equipping an item switches the entire image instead of attaching emoji overlays. Purchased accessories remain in the local SQLite profile and can be equipped or changed later. XP is the shop currency; coins remain separate.


Build 0.2.6 fixes an accessory display bug: equipped cosmetics are no longer clipped and now use item-specific positions. If an older page is still open, close it and restart the app using the updated package.
