# Visual design system

The portfolio uses one dark semantic palette across the web app. Components must consume these tokens instead of introducing local hex values.

## Color hierarchy

| Role | Token | Value | Use |
| --- | --- | --- | --- |
| Primary background | `--color-bg-primary` | `#080B12` | Page and application canvas |
| Secondary surface | `--color-bg-secondary` | `#111827` | Cards, panels, sidebar |
| Tertiary surface | `--color-bg-tertiary` | `#1E293B` | Hovered surfaces and raised states |
| Primary content | `--color-text-primary` | `#F8FAFC` | Headings and essential content |
| Secondary content | `--color-text-secondary` | `#94A3B8` | Paragraphs, metadata, supporting copy |
| Interaction | `--color-interaction` | `#8B5CF6` | Buttons, links, navigation, active states |
| Intelligence | `--color-intelligence` | `#22D3EE` | AI, data, models, technology indicators |
| Storytelling | `--color-storytelling` | `#F472B6` | Results, details, creative highlights |

## Usage rules

- Violet means the user can act or navigate.
- Cyan means the interface is explaining intelligence, data, or technology.
- Pink means the interface is adding narrative emphasis or a memorable detail.
- Color is never the only signal: active states also use borders, weight, labels, or position.
- Filled violet controls use dark text for contrast; white text on the brand violet is reserved for large display text or replaced with a darker violet when needed.
- New components must use semantic tokens from `src/shared/design-system/tokens.css`.
