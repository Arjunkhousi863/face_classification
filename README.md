# Face Classification + Attendance

Face Detection → Embedding (InsightFace) → Vector Search (pgvector) → **Mark Present**

## What you get

| Feature | Endpoint |
|--------|----------|
| Register user + face | `POST /users/register` |
| Search face + optional attendance | `POST /users/search` |
| Get / list / update / delete users | `GET/PUT/DELETE /users...` |
| Attendance list & stats | `GET /attendance`, `GET /attendance/stats` |
| Login (JWT) | `POST /auth/login` |
| Health | `GET /health` |

**Attendance rule:** when search finds a match and `mark_attendance=true` (default), that user is marked **Present** for today (one row per user per date).

---

## URLs / credentials you must add

Copy `.env.example` → `.env` and fill these.

### 1) PostgreSQL + pgvector (required)

| Variable | Where to get it |
|----------|-----------------|
| `DATABASE_URL` | **Supabase**: Project → Settings → Database → URI (`postgresql://...`) |
| | **Neon**: Dashboard → Connection string |
| | Local: `postgresql://postgres:postgres@localhost:5432/face_db` (docker-compose) |

Enable extension once (app also runs `CREATE EXTENSION IF NOT EXISTS vector`):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Use the **direct** connection string (not pooler-only) if you hit prepared-statement issues on serverless poolers.

### 2) Cloudinary (required for photos)

| Variable | Where |
|----------|--------|
| `CLOUDINARY_CLOUD_NAME` | [console.cloudinary.com](https://console.cloudinary.com) → Settings → API Keys |
| `CLOUDINARY_API_KEY` | same |
| `CLOUDINARY_API_SECRET` | same |

### 3) Auth / app

| Variable | Notes |
|----------|--------|
| `JWT_SECRET` | Long random string |
| `CORS_ORIGINS` | Frontend origins, comma-separated e.g. `http://localhost:5173,https://your-app.onrender.com` |
| `FACE_MATCH_THRESHOLD` | Max cosine **distance** for a match (default `0.45`). Tune after tests. |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Seeded on first boot |

### 4) Frontend

| Variable | Notes |
|----------|--------|
| `VITE_API_URL` | Public FastAPI URL in production, e.g. `https://face-api.onrender.com`. Locally omit and use Vite `/api` proxy. |

### 5) Deploy URLs (Render)

| Piece | URL type |
|-------|----------|
| FastAPI Web Service | `https://YOUR-API.onrender.com` |
| React Static Site | `https://YOUR-WEB.onrender.com` |
| Set `CORS_ORIGINS` = React URL | |
| Set `VITE_API_URL` = FastAPI URL | rebuild frontend after change |

No AWS/S3 needed for MVP. Optional later: S3 instead of Cloudinary.

---

## Local run

### Backend

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edit .env
uvicorn app.main:app --reload --port 8000
```

First InsightFace run downloads `buffalo_l` models (needs network).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — login `admin` / `admin123` (or your `.env` values).

### Docker DB only

```bash
docker compose up db -d
```

---

## Attendance API usage

```http
POST /users/search
Content-Type: multipart/form-data
Authorization: Bearer <token>

image: <file>
mark_attendance: true
```

**Found + attendance:**

```json
{
  "found": true,
  "similarity": 0.92,
  "user": { "user_id": "USR0001", "name": "..." },
  "attendance_marked": true,
  "attendance_message": "Attendance marked present for ..."
}
```

**Not found:**

```json
{ "found": false, "message": "No matching face found" }
```

List:

```http
GET /attendance?attendance_date=2026-08-02&page=1&limit=20
GET /attendance/stats?attendance_date=2026-08-02
```

---

## Roles

| Role | Can |
|------|-----|
| `admin` | All + delete users |
| `officer` | Register, search, update, view attendance |
| `viewer` | Search (attend), list users, view attendance |

---

## Project layout

```
app/
  main.py
  config.py
  routers/     users, search, attendance, auth, health
  models/      user, embedding, attendance, search_log
  services/    face, embedding, cloudinary, attendance
  ...
frontend/      React (Dashboard, Register, Search, Users, Attendance)
```

## Tune matching

InsightFace embeddings use cosine distance via pgvector `<=>`.

- `similarity = 1 - distance`
- Match if `distance <= FACE_MATCH_THRESHOLD`

Start at `0.45`, then tighten/loosen after real photos.
