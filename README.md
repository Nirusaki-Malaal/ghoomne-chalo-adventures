# Ghoomne Chalo Adventures

A FastAPI + Jinja2 travel website with:

- dynamic package listing from MongoDB
- SEO-friendly static endpoints (`robots.txt`, `sitemap.xml`, etc.)
- admin panel with JWT cookie auth
- add/edit/delete package management
- optional Cloudinary image upload (base64 -> hosted URL)
- Vercel serverless deployment support

This project serves rendered HTML pages (not a SPA) and keeps package content in MongoDB for easy updates from the admin dashboard.

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [How It Works](#how-it-works)
4. [API and Page Routes](#api-and-page-routes)
5. [Data Model (Package Schema)](#data-model-package-schema)
6. [Environment Variables](#environment-variables)
7. [Local Development Setup](#local-development-setup)
8. [Run Commands](#run-commands)
9. [Admin Workflow](#admin-workflow)
10. [Image Handling Flow](#image-handling-flow)
11. [Deployment on Vercel](#deployment-on-vercel)
12. [Caching and Performance Notes](#caching-and-performance-notes)
13. [Security Notes](#security-notes)
14. [Useful Maintenance Scripts](#useful-maintenance-scripts)
15. [Troubleshooting](#troubleshooting)
16. [Future Improvements](#future-improvements)

## Tech Stack

- **Backend**: FastAPI
- **Templating**: Jinja2
- **Database**: MongoDB (Motor async client)
- **Auth**: JWT stored in `httponly` cookie
- **File/Image Hosting**: Cloudinary (optional)
- **Server**: Uvicorn (local), Vercel Python runtime (production)

Dependencies (from `requirements.txt`):

- `fastapi`
- `uvicorn`
- `jinja2`
- `motor`
- `PyJWT`
- `python-dotenv`
- `python-multipart`
- `aiofiles`
- `cloudinary`

## Project Structure

```text
.
├── main.py                  # FastAPI app, routes, auth, DB access
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel build/rewrites/cache headers
├── templates/               # Jinja templates
│   ├── index.html
│   ├── packages.html
│   ├── admin.html
│   ├── edit_package.html
│   ├── login.html
│   └── error.html
├── statics/
│   ├── css/                 # styling files
│   ├── js/                  # frontend scripts
│   ├── assets/              # images/icons
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── llms.txt
│   └── humans.txt
└── plugins/                 # one-off helper scripts (most are migration/legacy)
```

## How It Works

1. App starts in `main.py`.
2. `.env` variables are loaded via `python-dotenv`.
3. MongoDB connection is created (`ghoomne_chalo.packages`).
4. Static files are mounted at `/statics`.
5. Public pages fetch packages from MongoDB and render via Jinja templates.
6. Admin login sets a JWT in `admin_token` cookie.
7. Protected admin routes require valid JWT and allow add/edit/delete package entries.

## API and Page Routes

### Public

- `GET /` -> Homepage (`index.html`) with dynamic package data
- `GET /packages` and `GET /packages/` -> Packages listing page (`packages.html`)
- `GET /api/packages` -> JSON object of packages keyed by `package_id`

### SEO / Bot Files

- `GET /robots.txt`
- `GET /sitemap.xml`
- `GET /llms.txt`
- `GET /humans.txt`
- `GET /favicon.ico`

### Auth

- `GET /login` -> Admin login page
- `POST /login` -> Validates credentials, sets JWT cookie, redirects to `/admin`
- `GET /logout` -> Clears cookie and redirects to `/login`

### Admin (Protected)

- `GET /admin` -> Admin dashboard
- `POST /admin/add` -> Add package
- `POST /admin/delete/{pkg_id}` -> Delete package
- `GET /admin/edit/{package_id}` -> Edit package page
- `POST /admin/edit/{update_package_id}` -> Update package

### Error Handling

- Custom template-based handling for:
	- `404` (friendly not-found message)
	- `401/403` (access restriction message)
	- generic `500`
- Redirect-like exceptions (`301/302/303/307/308`) are passed through safely.

## Data Model (Package Schema)

Each package document typically includes:

```json
{
	"package_id": "harsil",
	"title": "Harsil Valley",
	"price": "₹8999",
	"badge": "Expert Choice",
	"summary": "...",
	"eyebrow": "3N / 4D ...",
	"card_image": "https://... or /statics/...",
	"image": "https://... or /statics/...",
	"facts": ["...", "..."],
	"itinerary": [
		{
			"day": "Day 1",
			"title": "...",
			"items": ["...", "..."]
		}
	],
	"highlights": ["..."],
	"inclusions": ["..."],
	"exclusions": ["..."],
	"carry": ["..."]
}
```

Notes:

- `facts`, `inclusions`, `exclusions`, `carry`, `highlights` are stored as arrays.
- Itinerary is parsed from text input format:
	- `Day X: Title`
	- bullet rows starting with `-`.

## Environment Variables

Create a `.env` file in project root.

Required:

- `MONGO_URI` -> MongoDB connection string

Recommended for production:

- `JWT_SECRET` -> secret key for signing admin JWTs
- `ADMIN_USER` -> admin username
- `ADMIN_PASS` -> admin password

Optional:

- `CLOUDINARY_URL` -> if set, base64 image uploads are pushed to Cloudinary

Example:

```env
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.xxx.mongodb.net/?retryWrites=true&w=majority
JWT_SECRET=replace_with_a_long_random_secret
ADMIN_USER=admin
ADMIN_PASS=change_me
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>
```

## Local Development Setup

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd ghoomne-chalo-adventures
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add `.env`

Use the env template above.

### 5. Start app

```bash
uvicorn main:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/packages`
- `http://127.0.0.1:8000/admin`

## Run Commands

```bash
# Run in dev mode
uvicorn main:app --reload

# Run on custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Admin Workflow

1. Visit `/login` and sign in with env credentials.
2. Dashboard (`/admin`) shows existing packages.
3. Add package form accepts:
	 - basic metadata
	 - image input
	 - long-form fields (itinerary, highlights, etc.)
4. Edit action opens `/admin/edit/{package_id}` with pre-filled values.
5. Delete action removes package by `package_id`.

## Image Handling Flow

When adding/updating package:

1. Frontend converts selected image into base64 string (hidden input).
2. Backend receives `card_image`.
3. If it starts with `data:image/` and Cloudinary is configured:
	 - uploads to Cloudinary
	 - stores secure URL in DB
4. Backend mirrors `card_image` into `image` for consistency.

## Deployment on Vercel

`vercel.json` is configured to:

- use `main.py` with `@vercel/python`
- rewrite all routes to `main.py`
- set long cache headers for static files
- set SWR caching for `/api/*`

### Steps

1. Push code to GitHub.
2. Import repository in Vercel.
3. Add environment variables in Vercel Project Settings:
	 - `MONGO_URI`
	 - `JWT_SECRET`
	 - `ADMIN_USER`
	 - `ADMIN_PASS`
	 - `CLOUDINARY_URL` (optional)
4. Deploy.

## Caching and Performance Notes

- GZip middleware enabled with `minimum_size=500`.
- Static assets are mounted and served from `/statics`.
- Vercel header rules cache static assets aggressively.
- `/api/*` gets stale-while-revalidate cache policy in Vercel.

## Security Notes

Important hardening recommendations:

1. **Never use default credentials in production.**
2. Set a strong random `JWT_SECRET`.
3. Consider adding:
	 - `secure=True` on cookies in production HTTPS
	 - rate limiting for `/login`
	 - CSRF protection on admin form endpoints
	 - audit logging for admin actions
4. Restrict database user permissions to least privilege.

## Useful Maintenance Scripts

Root scripts:

- `fix_js.py` -> helper script for JS theme behavior updates
- `fix_theme.py` -> helper script for theme logic in templates

Plugin scripts (`plugins/`):

- `seed_db.py` -> optional one-time DB seeding helper
- others are mostly one-off migration scripts and usually not part of runtime

## Troubleshooting

### `MONGO_URI not found in environment (.env)`

- Ensure `.env` exists in project root.
- Ensure `MONGO_URI=...` is defined.
- Restart server after env changes.

### Admin login keeps redirecting to `/login`

- Verify `JWT_SECRET`, `ADMIN_USER`, `ADMIN_PASS` values.
- Clear browser cookies and retry.
- Check system clock correctness (JWT expiry uses UTC).

### Images not rendering

- If using local static paths, ensure files exist under `/statics/assets`.
- If using Cloudinary URLs, verify `CLOUDINARY_URL` and upload success.

### Static CSS/JS wrong content-type on deployment

- Mimetype fallbacks are added in app startup.
- Ensure deployment is using current `main.py`.

## Future Improvements

1. Add Pydantic models + validation for package payloads.
2. Move duplicated parsing logic into shared utility functions.
3. Replace in-file defaults for admin credentials with required env vars.
4. Add automated tests for auth and package CRUD routes.
5. Add migration/versioning for package schema changes.

---

If you want, I can also generate:

1. a short contributor-focused `CONTRIBUTING.md`
2. a production hardening checklist file
3. a sample `.env.example` file