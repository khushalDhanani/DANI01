# AIRIS Insights Frontend

Expo/React Native frontend for AIRIS Insights.

The application provides responsive web/native interfaces for database
discovery, profiling, analysis, data-quality modules, and persisted analysis
runs exposed by the FastAPI backend.

## Stack

- Expo 57
- Expo Router
- React 19 / React Native
- TypeScript
- NativeWind / Tailwind CSS
- TanStack Query
- Axios
- Zustand
- Zod
- React Hook Form
- Lucide React Native

Exact versions are defined by `package.json` and `package-lock.json`.

## Structure

```text
frontend/
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
│   ├── hooks/
│   ├── lib/
│   ├── providers/
│   ├── schemas/
│   ├── store/
│   ├── types/
│   └── utils/
├── .env.example
├── package.json
└── tsconfig.json
```

Always inspect the current filesystem before relying on this summary.

## Setup

```bash
cp .env.example .env
npm install
```

Configure the backend API URL.

### Web / iOS Simulator

```env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Android Emulator

```env
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1
```

### Physical Device

```env
EXPO_PUBLIC_API_URL=http://<YOUR_LAN_IP>:8000/api/v1
```

`EXPO_PUBLIC_*` values are bundled into the client. Never store secrets in
frontend environment variables.

## Run

```bash
npm run start
```

Targets:

```bash
npm run web
npm run android
npm run ios
```

## Data Flow

Server state follows:

```text
Route / Feature View
        ↓
TanStack Query Hook
        ↓
API Module
        ↓
Shared Axios Client
        ↓
FastAPI /api/v1
```

Important conventions:

- routes/screens do not call Axios directly;
- TanStack Query owns server state;
- Zustand owns UI/client state only;
- API contracts are typed;
- query keys are centralized;
- backend URLs are centralized;
- loading/error/empty/success states are handled;
- large lists are paginated or virtualized.

## Data-Quality Semantics

The frontend must display the backend's canonical business definitions.

Do not independently recalculate data-quality qualification rules, authoritative
totals, or issue severity.

For example, if a backend issue is `critical`, `warning`, or `info`, the
frontend should consistently map that semantic value to the design system
instead of deriving severity differently on each screen.

## Validation

```bash
npm run typecheck
npm run lint
```

For web-impacting changes:

```bash
npm run build:web
```

To verify runtime startup:

```bash
npm run start
```

There is currently no dedicated frontend unit-test script in `package.json`.
Do not assume a test framework exists.

## Responsive / Accessibility Expectations

The app targets mobile, tablet, and web.

- use established breakpoint/layout utilities;
- avoid fixed mobile-only dimensions;
- virtualize large lists;
- add labels/roles to icon-only interactive controls where needed;
- do not rely on color alone for status/severity;
- preserve keyboard usability on web.

## Agent Instructions

Read:

1. [`../AGENTS.md`](../AGENTS.md)
2. [`AGENTS.md`](AGENTS.md)

before modifying frontend code.

`CLAUDE.md` intentionally redirects to `AGENTS.md` so instructions remain
single-source.
