# Product definition

## Product statement

AI Portfolio Engine is an open-source platform that transforms professional knowledge written in Markdown into a dynamic portfolio, hybrid search, and an AI assistant grounded in verifiable evidence.

## Users

- Portfolio owner: maintains knowledge and controls publication.
- Portfolio visitor: explores projects, experience, skills, and evidence.
- Open-source developer: runs the system with fictional example content.

## Core user journey

1. A developer writes or updates a Markdown document.
2. The engine validates and indexes only changed sections.
3. Portfolio pages and search use the updated content.
4. Chat retrieves public evidence and cites sources.
5. If evidence is insufficient, the assistant says so instead of inventing a claim.

## Non-goals for V1

- Autonomous multi-agent systems.
- Generic personal knowledge management.
- Private content exposed through the public API.
- A full CMS before ingestion is reliable.
- Supporting every source format at once.

## Success criteria

- A new developer can run the example system with Docker Compose.
- A Markdown change can be indexed incrementally.
- Exact and semantic searches both work.
- Public chat answers include inspectable citations.
- Unsupported questions result in a safe no-evidence response.
- The same content powers portfolio pages and chat.
