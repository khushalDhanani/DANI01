# AIRIS Insights — Frontend Agent Instructions

These rules apply to `frontend/`.

Read the repository root [`AGENTS.md`](../AGENTS.md) first.

## Frontend Scope

Expo/React Native/TypeScript application for AIRIS Insights, targeting web and
native platforms.

Dependency versions are defined in `package.json` and `package-lock.json`.

Current major stack:

- Expo 57 / Expo Router
- React 19 / React Native
- TypeScript
- NativeWind / Tailwind
- TanStack Query
- Axios
- Zustand
- Zod
- React Hook Form
- Lucide React Native

When changing Expo/Expo Router/NativeWind configuration, use documentation
matching the installed Expo SDK/version rather than generic or outdated Expo
guidance.

## Inspect Current Structure First

The project evolves. Never rely on an old route-tree example without checking
the filesystem.

Current high-level layout:

```text
frontend/
├── __tests__/
│   ├── api/
│   ├── hooks/
│   ├── features/
│   └── routes/
├── app/
│   ├── _layout.tsx
│   └── (shell)/
│       ├── _layout.tsx
│       ├── index.tsx
│       ├── analysis/
│       ├── database/
│       ├── daylite/
│       └── modules/
├── src/
│   ├── api/
│   ├── components/
│   ├── constants/
│   ├── features/
│   │   ├── analysis/
│   │   ├── classification/
│   │   ├── dashboard/
│   │   ├── explorer/
│   │   ├── modules/
│   │   ├── profiling/
│   │   └── table-details/
│   ├── hooks/
│   ├── lib/
│   ├── providers/
│   ├── schemas/
│   ├── store/
│   ├── types/
│   └── utils/
├── .env.example
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

Do not place tests inside `app/` because Expo Router treats files there as route entries. All test suites belong inside `__tests__/`.

# 1. Mandatory Server-Data Flow

Server data must follow:

```text
Route / Feature View
        ↓
TanStack Query Hook
        ↓
API Domain Module
        ↓
Shared apiClient
        ↓
FastAPI /api/v1/...
```

Rules:

- routes/screens do not call Axios directly;
- routes/screens do not call `apiClient` directly;
- API modules call the shared `apiClient`;
- hooks call API modules;
- API modules contain transport mapping, not UI logic;
- hooks contain query/mutation orchestration, not JSX.

# 2. API Client

Use one shared Axios instance from `src/api/client.ts`.

The base URL comes from centralized configuration sourced from
`EXPO_PUBLIC_API_URL`.

Do not hard-code backend URLs in routes, views, components, hooks, or feature
modules.

Do not create a second Axios instance unless architecture is explicitly changed.

Preserve the project's structured `ApiError` behavior.

# 3. Environment Variables

Frontend environment variables use the `EXPO_PUBLIC_` prefix and are bundled
into the client.

Never place secrets in frontend environment variables.

`EXPO_PUBLIC_API_URL` must be centralized through frontend configuration.

Remember:

- web/iOS simulator may use `localhost`;
- Android emulator uses host mapping such as `10.0.2.2`;
- physical devices require a reachable LAN/backend address.

When environment behavior changes, update `.env.example`.

# 4. TanStack Query Owns Server State

TanStack Query is the source of truth for API/server state.

Do not mirror API responses into Zustand.

Query keys must be centralized in the existing `QUERY_KEYS` structure.

Include all parameters that affect a request in its query key.

Every data-displaying view must intentionally handle:

- loading;
- error;
- empty;
- success.

Do not hide a failed request by rendering an empty successful state.

# 5. Zustand Is Client/UI State Only

Use Zustand only for state that is truly local/client-side, such as UI
selection/filter/navigation state that is not the authoritative backend result.

Do not:

- cache API results in Zustand;
- mirror TanStack Query data;
- store authoritative server totals in Zustand.

# 6. Zod

Use runtime schemas at meaningful external boundaries, for example:

- form validation;
- untrusted external input;
- API payloads where schema drift is a real risk.

Follow the project's existing Zod import/validation convention.

Do not add schemas merely because Zod is installed.

# 7. TypeScript

`strict` mode is required.

Do not weaken TypeScript configuration to make a change compile.

Forbidden:

- explicit `any`;
- `@ts-ignore`;
- `@ts-nocheck`.

Prefer:

- explicit request/response interfaces;
- `unknown` followed by validation/narrowing;
- type unions;
- `import type` for type-only imports.

Backend request/response shapes used by the frontend must have corresponding
typed contracts under `src/types/` or the established domain typing location.

# 8. Backend Contract and Business Semantics

The frontend displays backend/domain truth; it must not reinvent backend
business definitions.

Do not independently recalculate:

- data-quality qualification predicates;
- authoritative issue totals;
- duplicate/missing/invalid definitions;
- active/deleted semantics;
- score meaning;
- issue severity.

If the backend returns semantic values such as `critical`, `warning`, or `info`,
map those values to presentation consistently. Do not infer a different severity
from counts in each screen.

If an API contract appears wrong, fix the backend/source contract where
appropriate instead of adding UI-specific compensation that creates divergence.

# 9. NativeWind / Styling

Use NativeWind utility classes for layout/spacing/styling where possible.

Use `StyleSheet`/inline style only for cases NativeWind cannot reasonably
express, especially dynamic numeric values.

Use existing theme/design tokens.

Do not scatter hard-coded colors, backend-dependent values, or repeated layout
constants across components.

`global.css` is the NativeWind entry point; do not turn it into a generic CSS
dumping ground.

## Icons

Do not use Unicode emoji as product UI icons.

Use the installed vector icon system (Lucide React Native) and semantic design
tokens.

# 10. Responsive Layout

Target:

- iOS;
- Android;
- tablet;
- web;
- desktop-width web.

Use the established `useBreakpoint`, `BREAKPOINTS`, and `LAYOUT` abstractions.

Do not hard-code a single-device width.

Data-heavy desktop screens should respect the project's maximum content width
and should remain usable on smaller screens.

# 11. Accessibility

Interactive controls must be understandable and operable beyond visual styling.

Where applicable:

- provide accessible labels for icon-only controls;
- use appropriate accessibility roles/state;
- maintain meaningful visible text;
- keep touch targets reasonably usable;
- preserve keyboard usability for web;
- avoid relying on color alone to convey severity/status;
- ensure critical/warning/info states have textual/semantic meaning as well.

# 12. Route Files

Files under `app/` are route entry points.

Keep route files thin.

Root/layout files own routing/provider/infrastructure composition, not domain
business logic.

Complex JSX, data orchestration, and feature behavior belong in
`src/features/<feature>/` and reusable hooks/components.

# 13. Components

Use functional components with typed props.

Prefer small, single-responsibility components.

Reusable presentational UI belongs under `src/components/`.

Feature-specific logic/views belong under `src/features/`.

Do not create 500-line mega-components or move feature business logic into a
generic shared component folder.

# 14. Data Volume & Performance

The backend analyzes a large database. Never assume lists are small.

Use:

- API pagination;
- server-provided totals;
- `FlatList`/virtualization where appropriate;
- bounded page sizes;
- cached parameterized queries.

Do not render all database rows/tables in a non-virtualized flat map when the
result can grow large.

Never derive authoritative totals from the current page.

# 15. Security & Data Sensitivity

Assume API payloads may include PII.

Do not display raw source values merely because they are available.

Do not log source row payloads in production.

Never put credentials or secrets in `EXPO_PUBLIC_*`.

Do not add source-data write/delete UI flows unless the project requirement
explicitly changes the repository-wide read-only invariant.

# 16. Adding Dependencies

Before adding a package:

1. check whether the existing stack already provides the capability;
2. verify Expo/React Native compatibility;
3. prefer the Expo-compatible installation path where applicable;
4. check compatibility with the installed Expo/React Native versions;
5. document why the dependency is necessary.

Do not add overlapping state, HTTP, validation, or styling frameworks without a
concrete architecture decision.

# 17. Frontend Testing / Validation

Frontend unit and integration testing is powered by **Vitest** and **React Testing Library**.

Required validation for frontend changes:

```bash
npm run test
npm run typecheck
npm run lint
```

For changes that can affect web routing, bundling, shared configuration, styles,
or web rendering, also run:

```bash
npm run build:web
```

Ensure the Expo dev server starts for meaningful runtime changes:

```bash
npm run start
```

When creating or modifying frontend features, hooks, or complex UI components, add focused behavioral unit/integration tests in Jest (`jest-expo` and React Native Testing Library) under `__tests__/` (`*.test.ts` or `*.test.tsx`).

# 18. What Not to Do

| Forbidden | Use Instead |
|---|---|
| Axios directly in a screen | Query hook → API module |
| A second Axios client | Shared `apiClient` |
| `any` | Explicit type / `unknown` + narrowing |
| `@ts-ignore` | Fix the type |
| Hard-coded backend URL | Centralized API config |
| Zustand for API results | TanStack Query |
| Client-derived authoritative totals | API-provided totals |
| Recalculating backend quality rules | Backend semantic contract |
| Emoji UI icons | Lucide vector icons |
| Huge non-virtualized lists | Pagination/virtualization |
| Mega-components | Feature/component decomposition |
| Generic utility dumping ground | Domain-scoped helper modules |
| Unrelated refactors | Focused change |
| Unjustified package | Existing stack / justified dependency |

# 19. Frontend Definition of Done

A frontend change is complete only when relevant items below are satisfied:

- [ ] `npm run typecheck` passes with zero type errors;
- [ ] `npm run lint` passes with zero errors and zero warnings (`--max-warnings=0`);
- [ ] `npm test` passes (Jest component, hook, and API tests in `__tests__/`);
- [ ] `npm run build:web` passes for web-impacting changes;
- [ ] new feature/behavior includes corresponding tests in `__tests__/` (hooks, API, components, empty/loading/error states);
- [ ] Expo starts for meaningful runtime changes;
- [ ] affected routes render correctly on an appropriate target;
- [ ] loading/error/empty/success states are handled;
- [ ] large lists remain bounded/virtualized;
- [ ] authoritative totals come from the API;
- [ ] backend business predicates/severity are not duplicated client-side;
- [ ] new API contracts are typed;
- [ ] query keys include request-defining parameters;
- [ ] accessibility is considered for changed interactive/status UI;
- [ ] no `any`, type suppression, hard-coded backend URL, secret, or raw debug
      PII was introduced;
- [ ] backend/frontend contracts remain synchronized.
