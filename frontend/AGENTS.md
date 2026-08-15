# AIRIS Insights — Frontend Agent Rules

> **Expo has changed.** Before writing code involving Expo, Expo Router, or NativeWind configuration,
> read the exact versioned docs at https://docs.expo.dev/versions/v57.0.0/

---

## Stack (verified installed versions)

| Package | Version |
|---|---|
| Expo | `~57.0.12` |
| Expo Router | `~57.0.12` |
| React Native | `0.86.2` |
| TypeScript | `~6.0.3` |
| NativeWind | `^4.2.6` + `tailwindcss ^3.4.19` |
| TanStack Query | `^5.101.4` |
| Axios | `^1.19.0` |
| Zustand | `^5.0.15` |
| Zod | `^3.25.76` |

---

## Project Layout (actual — do not invent directories)

```
frontend/
├── app/                     # Expo Router routes only — thin files
│   ├── _layout.tsx          # Infrastructure only: CSS, QueryProvider, Stack
│   └── index.tsx            # Home/foundation screen
│
├── src/
│   ├── api/                 # Axios modules — one file per backend domain
│   │   ├── client.ts        # Single shared Axios instance + ApiError class
│   │   ├── health.api.ts
│   │   ├── database.api.ts
│   │   ├── table.api.ts
│   │   └── analysis.api.ts
│   │
│   ├── components/          # Reusable, presentational components
│   │   ├── ui/              # Atomic UI (badges, cards, buttons)
│   │   ├── layout/          # App shell, header, nav
│   │   ├── database/        # Database-domain display components
│   │   ├── tables/          # Table-domain display components
│   │   └── charts/          # Chart wrappers (future)
│   │
│   ├── constants/
│   │   ├── config.ts        # API_CONFIG, ENV, QUERY_KEYS — single source of truth
│   │   ├── layout.ts        # BREAKPOINTS, LAYOUT dimensions
│   │   └── theme.ts         # Design tokens
│   │
│   ├── features/            # Self-contained feature modules
│   │   ├── dashboard/
│   │   ├── explorer/        # 970-table database explorer
│   │   ├── table-details/
│   │   ├── profiling/
│   │   └── classification/
│   │
│   ├── hooks/               # TanStack Query hooks + useBreakpoint + useUIStore
│   │   ├── useHealth.ts
│   │   ├── useDatabase.ts
│   │   ├── useTable.ts
│   │   ├── useAnalysis.ts
│   │   ├── useBreakpoint.ts
│   │   └── useUIStore.ts    # Re-exports from src/store/useUIStore
│   │
│   ├── lib/
│   │   ├── utils.ts         # Narrow, named helpers — not a dumping ground
│   │   └── validation.ts    # Zod re-export: import { z } from "@/lib/validation"
│   │
│   ├── providers/
│   │   └── query-provider.tsx
│   │
│   ├── schemas/             # Zod schemas — add when runtime validation is needed
│   ├── store/
│   │   └── useUIStore.ts    # Zustand — UI/client state only
│   ├── types/               # Shared TypeScript interfaces mirroring FastAPI responses
│   └── utils/               # Utility functions scoped by domain (e.g. formatters.ts)
│
├── global.css               # NativeWind: @tailwind base/components/utilities
├── tailwind.config.js       # presets: [nativewind/preset], content: app/**, src/**
├── metro.config.js          # withNativeWind(config, { input: "./global.css" })
├── babel.config.js          # jsxImportSource: "nativewind" + "nativewind/babel"
├── nativewind-env.d.ts      # /// <reference types="nativewind/types" />
├── tsconfig.json            # strict: true, paths: { "@/*": ["./src/*"] }
├── eslint.config.mjs        # Flat config — no-explicit-any: error
├── .env                     # EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
└── .env.example             # Documented variants for device/emulator/LAN
```

---

## Rules

### 0. Inspect Before You Touch

- **Read existing files** before modifying. Check what is already imported, exported, and typed.
- Run `npx tsc --noEmit` and `npx eslint src/ app/ --ext .ts,.tsx` before and after changes.
- Never assume a file, export, or component exists — verify with the filesystem.

### 1. Mandatory Data Flow

Every data request **must** follow this chain exactly:

```
Screen / Route
    ↓
TanStack Query hook  (src/hooks/)
    ↓
API module           (src/api/*.api.ts)
    ↓
apiClient            (src/api/client.ts)
    ↓
FastAPI backend      (/api/v1/...)
```

- **Screens** call hooks only — never `axios.get(...)` or `apiClient` directly.
- **API modules** call `apiClient` only — no business logic, no formatting.
- **Hooks** call API modules — no UI, no JSX.

### 2. API Client

- One shared instance: `apiClient` from `src/api/client.ts`.
- Base URL always from `API_CONFIG.BASE_URL` (sourced from `EXPO_PUBLIC_API_URL`).
- Never hard-code `localhost:8000` or any URL in a component or screen.
- Errors surface as `ApiError` instances with `.status`, `.isNetworkError`, `.isTimeout`.
- Do not create a second Axios instance.

### 3. Environment Variables

- All env vars are prefixed `EXPO_PUBLIC_` — they are baked in at Metro bundler time.
- Read via `process.env.EXPO_PUBLIC_API_URL` — centralized in `src/constants/config.ts` only.
- On physical devices, `localhost` does not work. Document the LAN IP alternative in `.env.example`.

### 4. TanStack Query

- `QueryClient` is configured once in `src/providers/query-provider.tsx` with:
  - `retry: 1`, `staleTime: 30s`, `gcTime: 5min`, `refetchOnWindowFocus: false`, `refetchOnReconnect: true`
- All query keys live in `QUERY_KEYS` in `src/constants/config.ts`.
- Never duplicate server data (tables list, schema data, analysis results) into Zustand.
- Handle all four states in every data-displaying component: **loading**, **error**, **empty**, **success**.

### 5. Zustand — Client State Only

- `useUIStore` (`src/store/useUIStore.ts`) holds only pure client/UI state:
  - `selectedSchema`, `searchQuery`, `tableSortBy`, `tableSortDir`
- Add to Zustand only when the state is truly local/UI, not derivable from server data.
- Never cache or mirror API responses in Zustand.

### 6. Zod — Validation Where Needed

- Import `z` from `@/lib/validation` (not directly from `"zod"`).
- Schemas go in `src/schemas/` named `*.schema.ts`.
- Add schemas only when runtime validation of an external boundary is justified (e.g. form input, API response where schema drift is a risk).
- Do not create schemas just to use the package.

### 7. TypeScript

- `strict: true` is enforced in `tsconfig.json` — do not weaken it.
- `any` is banned (`@typescript-eslint/no-explicit-any: error`). Use `unknown`, typed interfaces, or type unions.
- `@ts-ignore` and `@ts-nocheck` are forbidden.
- Use `import type` for type-only imports.
- Prefix intentionally unused destructured variables with `_` (e.g. `_isFetching`).
- All API request params and response shapes must have a TypeScript interface in `src/types/`.

### 8. NativeWind / Styling & Iconography

- Style with `className` and NativeWind utility classes. Do not use `StyleSheet.create` for layout or spacing.
- Use `StyleSheet` or inline `style` only when NativeWind cannot express the property (e.g. dynamic numeric widths).
- Custom design tokens are in `tailwind.config.js` under `theme.extend.colors` (e.g. `dark-bg`, `dark-card`, `dark-border`). Use them.
- Never hard-code hex colors or pixel values inline — reference tokens or `LAYOUT` constants.
- `global.css` is the NativeWind entry point. Do not add unrelated CSS there.
- **No Emoji Icons**: Never use Unicode emojis (e.g. 📊, 🗄️, ⚡, 🔍, 🚀, 📁) for iconography or UI badges. Always use vector icons from `lucide-react-native` with semantic colors from `THEME_COLORS` or Tailwind classes.

### 9. Responsive Layout

- Use `useBreakpoint()` from `@/hooks/useBreakpoint` for layout decisions.
- Use `BREAKPOINTS` and `LAYOUT` from `@/constants/layout` for pixel thresholds and `MAX_CONTENT_WIDTH`.
- Data-heavy screens (table explorer, analysis runs) must cap content width on desktop with `maxWidth: LAYOUT.MAX_CONTENT_WIDTH`.
- Do not hard-code `width: 375` or any mobile-only dimension.
- Target: iOS, Android, Web browser, tablet, desktop-width web.

### 10. Route Files

- Files under `app/` are route entry points only. Keep them thin.
- `app/_layout.tsx` responsibilities: `global.css` import, `QueryProvider`, `StatusBar`, `Stack`. Nothing else.
- Business logic, data fetching, and complex JSX belong in `src/features/<feature>/`.
- A route file should render a feature view component and pass route params — nothing more.

### 11. Components

- Functional components with typed props interfaces only. No class components.
- Small, single-responsibility components. If a component exceeds ~150 lines, decompose it.
- Components in `src/components/` are reusable and presentational — no data fetching.
- Feature-specific views live in `src/features/<feature>/` and may call hooks.
- Do not put feature logic in `src/components/`.

### 12. Data Volume & Performance

- The database has **970+ tables**. Never render all rows in a flat list.
- Use `offset`/`limit` pagination via `API_CONFIG.DEFAULT_PAGE_SIZE = 25` or `FlatList` with virtualization.
- Always show counts and totals from the API — do not compute them client-side from partial pages.
- Use `QUERY_KEYS.DATABASE.TABLES(params)` with filter/sort/pagination params so each view is individually cached.

### 13. Security & Data Sensitivity

- Do not render raw PII values (personal names, IDs, email addresses) from column samples without a deliberate decision.
- Do not log API responses containing row data to the console in production (`ENV.IS_DEV` guard).
- The backend is read-only. Do not add write/delete operations to the API client without explicit instruction.

### 14. What Not to Do

| ❌ Forbidden | ✅ Instead |
|---|---|
| `axios.get(...)` in a screen | Call a hook; hook calls API module |
| `any` type | Typed interface or `unknown` |
| `@ts-ignore` | Fix the type properly |
| Hard-coded `http://localhost:8000` | `API_CONFIG.BASE_URL` |
| Zustand for server data | TanStack Query cache |
| Mega-component (500+ lines) | Decompose into feature subcomponents |
| Generic `utils.ts` accumulation | Scoped file e.g. `formatters.ts`, `dates.ts` |
| Rendering 970 rows at once | Paginate; use `FlatList` |
| Emoji icons (📊, 🗄️, ⚡) | Vector icons from `lucide-react-native` |
| Inventing backend data / mock | Only mock when explicitly requested |
| Refactoring unrelated working code | Minimal, focused changes |
| Adding a dependency without reason | Justify against existing stack |

### 15. Adding Dependencies

Before adding any package:
1. Check if the existing stack already covers it (Zod, Axios, TanStack Query, NativeWind, Zustand).
2. Check Expo compatibility with `expo install <package>`.
3. Do not add packages that conflict with `react-native@0.86.2` or `expo@57`.

---

## Definition of Done

A change is complete only when **all** of the following pass:

- [ ] `npx tsc --noEmit` exits with **0 errors**
- [ ] `npx eslint src/ app/ --ext .ts,.tsx` exits with **0 errors, 0 warnings**
- [ ] `npm run start` (Expo dev server) starts without errors
- [ ] All affected routes/screens render correctly on at least one platform
- [ ] Loading, error, empty, and success states are handled in every data-displaying component
- [ ] No regressions in unaffected screens or routes
- [ ] Query keys for new data are registered in `QUERY_KEYS` in `src/constants/config.ts`
- [ ] New API response shapes have a TypeScript interface in `src/types/`
- [ ] No `any`, `@ts-ignore`, or hard-coded backend URLs introduced
