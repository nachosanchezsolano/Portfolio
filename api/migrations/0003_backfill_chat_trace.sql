INSERT OR IGNORE INTO chat_sessions
  (session_id, visitor_id, started_at, last_seen_at, message_count, last_intent)
SELECT
  session_id,
  MAX(visitor_id),
  MIN(created_at),
  MAX(created_at),
  COUNT(*),
  NULL
FROM chat_observations
GROUP BY session_id;

INSERT OR IGNORE INTO chat_messages
  (message_id, session_id, visitor_id, turn_index, raw_question,
   sanitized_question, retrieval_query, intent, retrieved_context,
   response_prompt_system, response_prompt_user, final_answer, sources,
   context_count, latency_ms, status, created_at, correctness, feedback_note)
SELECT
  observation_id,
  session_id,
  visitor_id,
  (
    SELECT COUNT(*)
    FROM chat_observations previous
    WHERE previous.session_id = current_observation.session_id
      AND (previous.created_at < current_observation.created_at
        OR (previous.created_at = current_observation.created_at AND previous.observation_id <= current_observation.observation_id))
  ) - 1,
  question,
  question,
  question,
  intent,
  '[]',
  '',
  question,
  answer,
  '[]',
  context_count,
  latency_ms,
  'completed',
  created_at,
  correctness,
  feedback_note
FROM chat_observations current_observation;
