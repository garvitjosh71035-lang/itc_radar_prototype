# Render deployment — ITC RADAR v2

The package is designed to preserve the original Render topology while replacing the interface and synthetic analysis API.

## Backend

Build:

```text
cd backend && pip install -r requirements.txt
```

Start:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After deployment check:

```text
https://<backend>.onrender.com/health
```

It should return `status: healthy`, version `2.0.0`, and `mode: synthetic_demo`.

The interactive demo does not require Postgres to answer its case endpoints. That is intentional: optional infrastructure should not make the SIH demo fail during a cold start.

## Frontend

Build:

```text
cd frontend && npm install && npm run build
```

Publish directory:

```text
./frontend/build
```

Set this environment variable in the frontend service:

```text
VITE_API_URL=https://<backend>.onrender.com/api
```

Do not put a trailing endpoint such as `/demo/cases`; use the API root ending in `/api`.

## Replacement workflow

For a clean replacement of the existing repository files:

```bash
# from a fresh clone / backup branch
# copy this package into the repo root

git add -A
git commit -m "Redesign ITC Radar evidence console"
git push
```

Render should rebuild from the connected branch automatically if auto-deploy is enabled.

## Post-deploy smoke test

- Frontend loads with the warm cream/green hero and product preview.
- Evidence Console shows 9 synthetic cases.
- Backend chip changes to `API connected` after a successful call.
- `RC-0001` resolves to `Red + cluster`.
- `N1-TRADER` resolves to `Green` with physical detectors role-gated.
- `N5-ESTATE` resolves to `Green` even with 11 registrations because the premises is adequate.
- `N6-UNRES` does not use unresolved premises evidence for an adverse physical finding.

## If the backend is sleeping

Render free/low-cost services may cold-start. The frontend intentionally keeps its deterministic local case data visible and labels the run as a demo fallback until the API responds. This is a presentation-resilience feature, not a replacement for backend verification.
