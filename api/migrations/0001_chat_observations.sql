CREATE TABLE IF NOT EXISTS chat_observations (
  observation_id TEXT PRIMARY KEY,
  visitor_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  sources TEXT NOT NULL DEFAULT '',
  intent TEXT NOT NULL,
  context_count INTEGER NOT NULL,
  latency_ms REAL NOT NULL,
  created_at TEXT NOT NULL,
  correctness TEXT CHECK (correctness IN ('correct', 'incorrect', 'needs_review')),
  feedback_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_chat_observations_created_at
  ON chat_observations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_observations_visitor_id
  ON chat_observations(visitor_id);
