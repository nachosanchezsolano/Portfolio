-- Stable logical-question keys make retries independent of Worker instance.
CREATE TABLE IF NOT EXISTS chat_requests (
  request_key TEXT PRIMARY KEY,
  fingerprint TEXT NOT NULL,
  answer TEXT,
  expires_at INTEGER NOT NULL
);
