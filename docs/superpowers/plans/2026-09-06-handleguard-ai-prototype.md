# HandleGuard AI Prototype Implementation Plan

> **For agentic workers:** Execute task-by-task with TDD. Steps use checkbox syntax.

**Goal:** Ship a modular, enterprise-style HandleGuard AI prototype with 12 behaviour detectors, risk/incident engines, FastAPI, React dashboard, unit+integration tests, docs, and a pushed commit.

**Architecture:** Protocol-based perception, IoU tracker, YAML-configured behaviour detectors, separate risk vs confidence, SQLite persistence, tool-grounded assistant.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, SQLAlchemy, PyYAML, pytest, React 18, Vite, Tailwind CSS.

## Global Constraints

- Python 3.11+, no worker identity, no face recognition, no confirmed-damage claims
- Thresholds in YAML, not hardcoded
- Risk and confidence are separate scores
- Detector is injectable (tests never require GPU/YOLO)
- FastAPI prefix `/api`
- Frontend proxies `/api` to backend
- Secrets only via `.env`; never commit keys

---

## File map

Create the monorepo as specified in master plan §6, with production code under `handleguard/`, API under `apps/api/`, web under `apps/web/`, tests under `tests/`.

---

### Task 1: Foundation (config, geometry, tracking, pipeline core)

TDD: geometry, config loader, tracker, velocity, risk, all 12 behaviours, incident dedup, explanation, assistant guardrails.

### Task 2: Persistence + API

SQLAlchemy models, repositories, FastAPI routes, integration tests (video process → incident → review → analytics → assistant).

### Task 3: Dashboard

React Vite app: KPIs, incident list/detail, review actions, analytics, assistant, upload.

### Task 4: Docs, seed, verify, commit, push

README, architecture, API, privacy, behaviour taxonomy, risk model. Seed demo data. Run full test suite. Commit and push.

---
