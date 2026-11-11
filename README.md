# Job Application Tracker

A full-stack app for tracking job applications — statuses, companies, and
uploaded resumes/cover letters — built with FastAPI and React.

**Live demo:** https://job-application-tracker-seven-orcin.vercel.app

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, JWT auth, SQLite (Postgres-ready)
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Deployment:** Render (backend), Vercel (frontend)

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit DATABASE_URL and SECRET_KEY
uvicorn app.main:app --reload
alembic upgrade head            # apply database migrations
```

API docs available at `http://localhost:8000/api/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # defaults to localhost:8000, edit if needed
npm run dev
```

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```

## Deployment

- Backend deploys to **Render** via `render.yaml` (Blueprint deploy).
- Frontend deploys to **Vercel** with root directory set to `frontend`.
- After deploying, update `ALLOWED_ORIGINS` on Render to include your live
  Vercel URL, and `VITE_API_URL` in `frontend/.env.production` to point at
  your live Render URL.

## License

MIT — see [LICENSE](LICENSE).
