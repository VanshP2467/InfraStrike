# InfraStrike

An IR light gun based shooting game made using Pygame and Raspberry Pi 4.

---

## Table of Contents

- [About](#about)
- [Team](#team)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## About

InfraStrike is a physical shooting game that combines a custom IR light gun with a Raspberry Pi 4 and a Pygame-powered display. Players aim and shoot at on-screen targets; the Raspberry Pi detects IR pulses from the gun and feeds hit data into the game engine to drive scoring, feedback, and game progression.

---

## Team

Five developers are collaborating on this project, each owning a primary area of responsibility:

| # | Role | Primary Focus |
|---|------|---------------|
| 1 | **Hardware Lead** | IR gun circuit, Raspberry Pi GPIO wiring & drivers |
| 2 | **Game Engine Lead** | Pygame game loop, rendering pipeline, asset management |
| 3 | **IR Detection Lead** | IR signal capture, hit detection algorithm, calibration |
| 4 | **Game Mechanics Lead** | Scoring system, levels, difficulty, game-state machine |
| 5 | **UI/UX & Audio Lead** | Menus, HUD, visual effects, sound effects & music |

---

## Roadmap

All versions follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

- **MAJOR** – incompatible changes to the hardware interface or save/config format  
- **MINOR** – new features added in a backwards-compatible way  
- **PATCH** – backwards-compatible bug fixes and small tweaks  

Pre-release milestones live in the **v0.x** series; the first production-ready release is **v1.0.0**.

---

### v0.1.0 — Project Bootstrap *(Owner: all)*

> Goal: get a working skeleton that every team member can build on.

- [ ] Initialise Git repository with branch strategy (`main`, `dev`, feature branches)
- [ ] Add `README.md`, `LICENSE`, `.gitignore` (Python / Raspberry Pi)
- [ ] Define folder structure (`src/`, `assets/`, `tests/`, `docs/`, `hardware/`)
- [ ] Set up virtual environment and `requirements.txt` (`pygame`, `RPi.GPIO`, `pytest`)
- [ ] Add a minimal `main.py` that opens a Pygame window (Hardware Lead + Game Engine Lead)
- [ ] Document local-dev and Raspberry Pi setup instructions

---

### v0.2.0 — Core Game Loop *(Owner: Game Engine Lead)*

> Goal: a playable window with a basic render loop, no IR hardware needed yet.

- [ ] Implement `GameLoop` class (fixed time-step update + render)
- [ ] Add asset loader for sprites and fonts
- [ ] Create a placeholder target that appears at random positions
- [ ] Implement mouse-click hit detection as a stand-in for IR input
- [ ] Add basic frame-rate display (debug overlay)
- [ ] Write unit tests for game-loop timing

---

### v0.3.0 — IR Hardware Integration *(Owner: Hardware Lead + IR Detection Lead)*

> Goal: the Raspberry Pi can receive and decode IR pulses from the light gun.

- [ ] Design and document IR receiver circuit (schematic in `hardware/`)
- [ ] Write GPIO interrupt handler for IR pulse capture (`src/ir_receiver.py`)
- [ ] Implement NEC / custom IR protocol decoder
- [ ] Add calibration routine (map gun position to screen coordinates)
- [ ] Replace mouse-click stub with real IR hit events
- [ ] Write hardware-in-the-loop tests (mock GPIO for CI)

---

### v0.4.0 — Game Mechanics *(Owner: Game Mechanics Lead)*

> Goal: a complete, rule-driven game session with scoring and difficulty.

- [ ] Implement `ScoreManager` (points per hit, combo multiplier, miss penalty)
- [ ] Design and implement game-state machine (`MainMenu → Playing → Paused → GameOver`)
- [ ] Add multiple target types (static, moving, bonus, avoid)
- [ ] Implement time-limited rounds with a countdown timer
- [ ] Add difficulty levels (Easy / Medium / Hard) adjusting target speed and spawn rate
- [ ] Persist high scores to a local JSON file
- [ ] Write unit tests for scoring logic and state transitions

---

### v0.5.0 — UI / UX & Audio *(Owner: UI/UX & Audio Lead)*

> Goal: polished presentation — menus, HUD, visual feedback, and sound.

- [ ] Design and implement Main Menu screen (title, Play, High Scores, Quit)
- [ ] Build in-game HUD (score, timer, lives/ammo, combo counter)
- [ ] Add hit/miss visual effects (flash, particle burst)
- [ ] Add Game Over and High Score entry screens
- [ ] Integrate sound effects (gunshot, hit, miss, countdown beeps)
- [ ] Add background music with mute/volume control
- [ ] Ensure 60 fps rendering across all screens

---

### v0.6.0 — Multiplayer / Co-op Mode *(Owner: Game Mechanics Lead + Hardware Lead)*

> Goal: support two players with independent IR guns.

- [ ] Add second IR receiver channel on GPIO
- [ ] Extend `ScoreManager` to track per-player scores
- [ ] Add co-op and competitive game modes
- [ ] Update HUD to show split or shared scores
- [ ] Test simultaneous shots and resolve tie-break logic

---

### v0.7.0 — Quality, Performance & CI *(Owner: all)*

> Goal: production-quality code with automated checks.

- [ ] Achieve ≥80% test coverage (`pytest-cov`)
- [ ] Add linting / formatting (`flake8`, `black`)
- [ ] Set up GitHub Actions CI (lint → test on every push / PR)
- [ ] Profile and optimise rendering bottlenecks
- [ ] Cross-test on Raspberry Pi 4 hardware (at least 30 fps under load)
- [ ] Address all open bug reports and TODOs in code

---

### v1.0.0 — First Stable Release *(Owner: all)*

> Goal: a fully playable, documented, and distributable release.

- [ ] Freeze API between hardware layer and game engine
- [ ] Complete user-facing documentation (`docs/setup.md`, `docs/gameplay.md`)
- [ ] Create install script / systemd service for auto-start on boot
- [ ] Tag `v1.0.0` release on GitHub with release notes and binary assets
- [ ] Record a short demo video for the repository README

---

### Backlog / Future Ideas

| ID | Idea | Complexity |
|----|------|------------|
| B-1 | Bluetooth score syncing to mobile app | High |
| B-2 | Online leaderboard via REST API | High |
| B-3 | Custom level / target editor | Medium |
| B-4 | Recoil feedback via solenoid or rumble motor | Medium |
| B-5 | Automated target reloading hardware | High |

---

## Contributing

1. Pick a task from the roadmap above and create a feature branch: `git checkout -b feature/<short-description>`  
2. Open a draft Pull Request early so teammates can follow progress.  
3. All PRs require at least **one** review from another team member before merging into `dev`.  
4. `main` is protected — only merge from `dev` when a milestone is complete and CI passes.  
5. Update this README (tick the checkboxes ✅) when a task is finished. 
