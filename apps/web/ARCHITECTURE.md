# Frontend architecture

This frontend follows the vertical-slice model described in the linked guide: entities, services, stores, and components live together inside the feature that owns them.

Astro reserves `src/pages` for file-based routing, so the home slice lives in `src/features/home` rather than inside `src/pages/home`. This is the Astro-specific equivalent and keeps routing concerns separate from feature code.

```text
src/
├── pages/                         # Astro routing only
│   └── index.astro
├── features/
│   └── home/                      # vertical slice: portfolio home
│       ├── entities/              # application models and validation
│       ├── services/              # stateless external communication
│       ├── stores/                 # state and transitions
│       └── components/             # Astro presentation and interaction
├── shared/
│   └── design-system/             # framework-agnostic CSS tokens
└── styles/                        # global composition of the design system
```

The home slice now contains two UI modes: the portfolio chat view and section views (`projects`, `studies`, `career`, and `about`). Navigation changes the active panel while the same chat component moves into a compact dock, preserving the assistant as a persistent interaction layer instead of duplicating chat logic per section.

The page composes the feature; components do not own API details, stores do not know Astro, and services return typed entities. If a second page needs an abstraction, move it to `shared` only after the reuse is proven.
