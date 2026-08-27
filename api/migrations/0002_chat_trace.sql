CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id TEXT PRIMARY KEY,
  visitor_id TEXT NOT NULL,
  started_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  message_count INTEGER NOT NULL DEFAULT 0,
  last_intent TEXT
);

CREATE TABLE IF NOT EXISTS chat_messages (
  message_id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES chat_sessions(session_id),
  visitor_id TEXT NOT NULL,
  turn_index INTEGER NOT NULL,
  raw_question TEXT NOT NULL,
  sanitized_question TEXT NOT NULL,
  retrieval_query TEXT NOT NULL,
  intent TEXT NOT NULL,
  retrieved_context TEXT NOT NULL DEFAULT '[]',
  response_prompt_system TEXT NOT NULL,
  response_prompt_user TEXT NOT NULL,
  final_answer TEXT NOT NULL,
  sources TEXT NOT NULL DEFAULT '[]',
  context_count INTEGER NOT NULL,
  latency_ms REAL NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  correctness TEXT CHECK (correctness IN ('correct', 'incorrect', 'needs_review')),
  feedback_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_seen
  ON chat_sessions(last_seen_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_visitor
  ON chat_sessions(visitor_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
  ON chat_messages(session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_created
  ON chat_messages(created_at DESC);
