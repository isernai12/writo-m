# Writo

Production-ready, SEO-first blog platform with a single Docker-based Render deployment.

## Architecture
- **Frontend:** Next.js App Router (TypeScript)
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Render free tier)
- **Proxy:** Nginx inside Docker
- **Single domain:** `/api/*` routes to FastAPI, everything else to Next.js

## Repo Structure
```
/apps/web     # Next.js app
/apps/api     # FastAPI app
/nginx        # Nginx config template
Dockerfile
start.sh
```

## Environment Variables
```
DATABASE_URL
JWT_SECRET
REFRESH_SECRET
ADMIN_SEED_KEY
ADMIN_EMAIL
ADMIN_PASSWORD
ADMIN_FULL_NAME
API_INTERNAL_URL (optional, defaults to http://127.0.0.1:8000)
NEXT_PUBLIC_SITE_URL (optional, for canonical URLs)
```

## Local Development
1. Start Postgres and set env vars.
2. Install dependencies:
   - `pip install -r apps/api/requirements.txt`
   - `cd apps/web && npm install`
3. Run migrations:
   - `alembic -c apps/api/alembic.ini upgrade head`
4. Run seed:
   - `python -c "from app.db import SessionLocal; from app.seed import seed_defaults; db=SessionLocal(); seed_defaults(db); db.close()"`
5. Start services:
   - `uvicorn app.main:app --reload --port 8000`
   - `cd apps/web && npm run dev`

## Render Deployment
1. Create a Render **Web Service** (Docker).
2. Set environment variables.
3. Attach a Render PostgreSQL database.
4. Deploy.
