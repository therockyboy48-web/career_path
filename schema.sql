-- AI Student Career Intelligence Platform
-- Schema is plain SQL — works identically on local libSQL file and on Turso.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    career_goal TEXT,
    bio TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    proficiency TEXT NOT NULL DEFAULT 'beginner', -- beginner | intermediate | advanced
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    tech_stack TEXT, -- comma separated
    repo_url TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    extracted_skills TEXT, -- comma separated, AI-extracted
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    description TEXT,
    required_skills TEXT NOT NULL -- comma separated, weighted "skill:weight"
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_role_id INTEGER NOT NULL REFERENCES job_roles(id),
    match_score REAL NOT NULL,
    missing_skills TEXT, -- comma separated
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_role_id INTEGER REFERENCES job_roles(id),
    steps_json TEXT NOT NULL, -- JSON array of {skill, resources, order}
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'medium', -- easy | medium | hard
    question TEXT NOT NULL,
    ideal_answer TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interview_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES interview_questions(id),
    user_answer TEXT,
    score REAL,
    feedback TEXT,
    matched_keywords TEXT,      -- comma separated
    missing_keywords TEXT,      -- comma separated
    input_mode TEXT DEFAULT 'text',   -- voice | text
    flagged_inappropriate INTEGER DEFAULT 0,
    integrity_flag TEXT DEFAULT 'clean', -- clean | warning | high_risk
    integrity_reasons TEXT,     -- comma separated, human-readable
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    meta TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    event_type TEXT NOT NULL, -- hackathon | volunteering | competition | workshop
    organizer TEXT,
    description TEXT,
    mode TEXT DEFAULT 'online', -- online | offline | hybrid
    location TEXT,
    start_date TEXT,          -- free-text or ISO date, e.g. "Rolling / check site"
    registration_deadline TEXT,
    external_url TEXT NOT NULL,
    tags TEXT,                 -- comma separated skills/interests, used for matching
    is_recurring INTEGER DEFAULT 0, -- 1 = an ongoing platform/program rather than a single dated event
    created_by INTEGER REFERENCES users(id),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'interested', -- interested | enrolled
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, event_id)
);
