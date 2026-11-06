# Pathfinder — AI Student Career Intelligence Platform

A full-stack final-year project: students track their skills and projects,
get AI-style career-role matching with weighted skill-gap analysis, an
auto-generated learning roadmap, and interview practice with scoring.

**Stack:** React (Vite + Tailwind) · FastAPI (Python) · Turso / libSQL · rule-based AI engine

```
career-platform/
├── backend/          FastAPI app, SQL schema, AI matching/roadmap/scoring logic
└── frontend/          React app (Vite + Tailwind)
```

## Why this counts as "AI"

No paid LLM API key is required to run this end-to-end — the matching,
roadmap generation, resume skill-extraction, and interview scoring are all
implemented as a self-contained rule-based engine in `backend/app/ai/`.
That's deliberate: it makes the project runnable for free, and it's easy to
explain in a viva ("weighted skill-gap scoring", "keyword-overlap answer
grading"). If you later want to plug in a real LLM (e.g. the Anthropic or
OpenAI API) for smarter resume parsing or answer grading, `backend/app/ai/`
is exactly where that call would go — every other part of the app is
already wired to consume whatever that module returns.

## 1. Backend setup

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

The backend uses an **embedded libSQL file** (`local.db`) by default — no
account, no install, no PostgreSQL. It's created automatically on first run,
schema and all.

Visit `http://localhost:8000/docs` for interactive Swagger API docs.

### Switching to real Turso (for deployment)

1. Install the Turso CLI and run:
   ```bash
   turso db create career-platform
   turso db show career-platform          # gives you the URL
   turso db tokens create career-platform  # gives you the token
   ```
2. In `backend/.env`, set:
   ```
   TURSO_DATABASE_URL=libsql://career-platform-<your-org>.turso.io
   TURSO_AUTH_TOKEN=<token>
   ```
3. Restart the backend. No code changes needed — same SQL, same client, now
   talking to the cloud.

## 2. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env      # points at http://localhost:8000 by default
npm run dev
```

Visit `http://localhost:5173`.

## 3. What's implemented

| Feature | Where |
|---|---|
| Auth (register/login, JWT, bcrypt) | `backend/app/routers/auth.py` |
| Profile | `routers/users.py`, `frontend/src/pages/ProfilePage.jsx` |
| Skills tracker | `routers/skills.py`, `SkillsPage.jsx` |
| Projects log | `routers/projects.py`, `ProjectsPage.jsx` |
| Resume skill-extraction | `routers/resumes.py`, `ai/recommender.py::extract_skills_from_text` |
| Weighted job-role matching | `ai/recommender.py::rank_job_roles` |
| Learning roadmap generator | `ai/roadmap_generator.py` |
| Interview question bank + scoring | `ai/interview_scorer.py`, `routers/interviews.py` |
| Voice interview agent + keyword feedback + integrity checks | `hooks/useVoiceAgent.js`, `ai/moderation.py`, `ai/integrity.py` |
| Events & Opportunities hub | `routers/events.py`, `EventsPage.jsx` |
| Dashboard | `routers/users.py::dashboard`, `DashboardPage.jsx` |

Data model (`backend/app/schema.sql`): `users`, `skills`, `projects`,
`resumes`, `job_roles`, `recommendations`, `learning_roadmaps`,
`interview_questions`, `interview_attempts`, `events`,
`event_enrollments`, `activity_logs`.

Eight seeded job roles (Data Analyst, Frontend/Backend/Full Stack
Developer, ML Engineer, DevOps Engineer, Product Analyst, QA Engineer),
each with weighted required skills — edit `backend/app/ai/seed_data.py` to
add more roles or change weights.

### Events & Opportunities hub

Gives students awareness of hackathons, competitions, volunteering, and
workshops, with three things existing "just search Unstop" doesn't give you:

- **Skill-matched ranking** — events are scored against the student's
  tracked skills (`ai/recommender.py::match_events`), same weighted-overlap
  idea as job-role matching, so the most relevant opportunities surface
  first instead of a flat chronological list.
- **Enrollment tracking** — students mark something "Interested" or
  "Enrolling" and see it later under My List / their dashboard, so nothing
  gets lost in a bookmarks folder. (Actual registration still happens on
  the organizer's own site via the "View & register" link — this app can't
  submit forms on Devfolio/Unstop/etc. on the student's behalf.)
- **Crowd-sourced freshness** — any logged-in student can add a real
  opportunity they found via "+ Add an opportunity". This is the honest
  answer to "how do you keep event listings current without a live feed
  or paid API": the seed data ships with stable, well-known recurring
  platforms (Smart India Hackathon, Devfolio, Unstop, HackerEarth, MLH,
  Flipkart GRiD, GSSoC, iVolunteer, UN Volunteers, Smile Foundation) and
  the community adds specific dated events on top.

### Voice interview agent

The Interview Prep page now supports answering **out loud**, plus honesty
checks appropriate for self-practice:

- **Real speech capture** — uses the browser's native Web Speech API
  (`SpeechRecognition` for speech-to-text, `SpeechSynthesis` to read the
  question aloud). No external speech API key, no audio sent to a server —
  transcription happens entirely in the browser. Falls back to a typed
  answer automatically in browsers that don't support it (e.g. Firefox).
- **Inappropriate-content detection** — `ai/moderation.py` checks the
  transcript for profanity or dismissive non-answers before scoring. A
  flagged attempt scores 0 with a direct, professional nudge instead of
  being graded — it's still logged so a pattern is visible in history.
- **Keyword-level correction** — `ai/interview_scorer.py::keyword_breakdown`
  diffs the transcript against the ideal answer's key terms and returns
  what the student hit vs. missed, shown as two tag lists under the score
  rather than just a single number.
- **Cheating/integrity signals** — while the student is answering, the
  browser tracks tab switches, time spent away from the tab, and paste
  events (`hooks/useIntegrityTracking.js`); the backend turns these into a
  transparent `clean | warning | high_risk` flag with plain-English reasons
  (`ai/integrity.py`). This is a self-practice honesty nudge, not
  proctoring software — it doesn't block submission, block the account, or
  claim certainty; it just surfaces the signal so the student can course-correct.

## 4. Suggested viva talking points

- **Why Turso, not PostgreSQL:** SQLite-compatible SQL (simple to reason
  about and demo), generous free tier, but still a genuinely modern
  cloud/edge database rather than a local file — `backend/app/database.py`
  shows the exact same code path works for both.
- **Weighted matching, not just skill counting:** each job role's
  `required_skills` string encodes an importance weight per skill
  (`SQL:3,Excel:2`), so missing a critical skill hurts your match score
  more than missing a nice-to-have one — see `match_score()`.
- **Extensibility:** the whole AI layer is isolated in `backend/app/ai/`,
  so swapping the rule-based scorer for a real LLM call later is a
  contained change, not a rewrite.

## 5. Next steps if you want to extend this

- Real LLM integration for resume parsing / interview grading (swap the
  functions in `ai/interview_scorer.py` and `ai/recommender.py`).
- GitHub API integration to pull real repos into the Projects page.
- Deploy: backend to Render/Railway/Fly.io, frontend to Vercel/Netlify,
  database to Turso cloud (see step above).
