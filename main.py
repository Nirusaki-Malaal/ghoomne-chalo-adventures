from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import mimetypes
import os
import re
import secrets
import time
from urllib.parse import urlparse

import bleach
import certifi
import cloudinary
import cloudinary.utils
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Securely inject missing mimetypes for Vercel's serverless environment.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")

load_dotenv()

if os.environ.get("CLOUDINARY_URL"):
    cloudinary.config(url=os.environ.get("CLOUDINARY_URL"))


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} environment variable is not set")
    return value


def env_flag(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def parse_allowed_hosts(raw_value: str | None) -> list[str]:
    if raw_value:
        parsed = [host.strip() for host in raw_value.split(",") if host.strip()]
        if parsed:
            return parsed
    return [
        "ghoomnechalo.com",
        "www.ghoomnechalo.com",
        "*.ghoomnechalo.com",
        "ghoomnechaloadventures.com",
        "www.ghoomnechaloadventures.com",
        "*.ghoomnechaloadventures.com",
        "*.vercel.app",
        "localhost",
        "127.0.0.1",
    ]


def validate_lookerstudio_url(raw_value: str | None) -> str | None:
    if not raw_value:
        return None
    parsed = urlparse(raw_value.strip())
    if parsed.scheme != "https" or parsed.netloc != "lookerstudio.google.com":
        raise ValueError("LOOKER_STUDIO_EMBED_URL must point to https://lookerstudio.google.com")
    return raw_value.strip()


APP_SECRET = require_env("JWT_SECRET")
ADMIN_USER = require_env("ADMIN_USER")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
LEGACY_ADMIN_PASS = os.environ.get("ADMIN_PASS", "").strip()
if not ADMIN_PASSWORD_HASH and not LEGACY_ADMIN_PASS:
    raise ValueError("ADMIN_PASSWORD_HASH environment variable is not set")

PASSWORD_HASHER = PasswordHasher()
COOKIE_SECURE = env_flag("COOKIE_SECURE", "true")
TRUST_PROXY_HEADERS = env_flag("TRUST_PROXY_HEADERS", "false")
IS_PRODUCTION = env_flag("IS_PRODUCTION", "false") or os.environ.get("VERCEL_ENV", "").lower() == "production"

AUTH_COOKIE_NAME = "admin_session"
CSRF_COOKIE_NAME = "csrf_token"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
LOGIN_RATE_LIMIT_WINDOW_SECONDS = 15 * 60
LOGIN_RATE_LIMIT_MAX_FAILURES = 5
MAX_IMAGE_UPLOAD_BYTES = 15 * 1024 * 1024
ALLOWED_IMAGE_MIME_TYPES = {"image/gif", "image/jpeg", "image/png", "image/webp"}
CLOUDINARY_UPLOAD_FOLDER = os.environ.get("CLOUDINARY_UPLOAD_FOLDER", "ghoomne-chalo/packages").strip("/")
PACKAGE_ID_PATTERN = re.compile(r"^[a-z0-9_-]{3,64}$")
GOOGLE_SITE_VERIFICATION = os.environ.get(
    "GOOGLE_SITE_VERIFICATION",
    "hymEtFlDiIhyTHTRpRJ6xH7DSap45WiF8yMdZNcD2lY",
).strip()
GOOGLE_SITE_VERIFICATION_HTML_FILENAME = os.environ.get("GOOGLE_SITE_VERIFICATION_HTML_FILENAME", "").strip().lstrip("/")
GOOGLE_SITE_VERIFICATION_HTML_CONTENT = os.environ.get("GOOGLE_SITE_VERIFICATION_HTML_CONTENT", "")
LOOKER_STUDIO_EMBED_URL = validate_lookerstudio_url(os.environ.get("LOOKER_STUDIO_EMBED_URL"))
AUDIT_LOG_RETENTION_DAYS = max(int(os.environ.get("AUDIT_LOG_RETENTION_DAYS", "90")), 1)
ALLOWED_HOSTS = parse_allowed_hosts(os.environ.get("ALLOWED_HOSTS"))

MONGO_URI = require_env("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where(), tz_aware=True)
db = client.ghoomne_chalo
packages_collection = db.packages
sessions_collection = db.admin_sessions
login_attempts_collection = db.admin_login_attempts
audit_log_collection = db.admin_audit_log

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def coerce_utc_datetime(value: datetime | None) -> datetime | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def hash_value(value: str) -> str:
    return hashlib.sha256(f"{APP_SECRET}:{value}".encode("utf-8")).hexdigest()


def hash_user_agent(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent", "").strip()
    return hashlib.sha256(user_agent.encode("utf-8")).hexdigest() if user_agent else None


def normalize_ip(value: str | None) -> str:
    if not value:
        return "unknown"
    try:
        return ipaddress.ip_address(value.strip()).compressed
    except ValueError:
        return "unknown"


def get_client_ip(request: Request) -> str:
    if TRUST_PROXY_HEADERS:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        for candidate in forwarded_for.split(","):
            normalized = normalize_ip(candidate)
            if normalized != "unknown":
                return normalized
    client_host = request.client.host if request.client else None
    return normalize_ip(client_host)


def get_or_create_csrf_token(request: Request) -> tuple[str, bool]:
    existing_token = request.cookies.get(CSRF_COOKIE_NAME)
    if existing_token:
        return existing_token, False
    return secrets.token_urlsafe(32), True


def set_csrf_cookie(response: Response, csrf_token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=True,
        secure=COOKIE_SECURE,
        max_age=SESSION_TTL_SECONDS,
        path="/",
        samesite="strict",
    )


def clear_csrf_cookie(response: Response) -> None:
    response.delete_cookie(CSRF_COOKIE_NAME, path="/")


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=session_id,
        httponly=True,
        secure=COOKIE_SECURE,
        max_age=SESSION_TTL_SECONDS,
        path="/admin",
        samesite="strict",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(AUTH_COOKIE_NAME, path="/admin")


def build_template_context(request: Request, extra: dict | None = None) -> dict:
    context = {
        "request": request,
        "csp_nonce": getattr(request.state, "csp_nonce", ""),
        "google_site_verification": GOOGLE_SITE_VERIFICATION,
        "analytics_embed_url": LOOKER_STUDIO_EMBED_URL,
    }
    if extra:
        context.update(extra)
    return context


def render_template(
    request: Request,
    name: str,
    context: dict | None = None,
    status_code: int = 200,
    include_csrf: bool = False,
) -> HTMLResponse:
    response_context = build_template_context(request, context)
    should_set_cookie = False
    if include_csrf:
        csrf_token, should_set_cookie = get_or_create_csrf_token(request)
        response_context["csrf_token"] = csrf_token

    response = templates.TemplateResponse(
        request=request,
        name=name,
        context=response_context,
        status_code=status_code,
    )
    if include_csrf and should_set_cookie:
        set_csrf_cookie(response, response_context["csrf_token"])
    return response


def validate_csrf(request: Request, form_token: str) -> None:
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME, "")
    if not cookie_token or not form_token or not secrets.compare_digest(cookie_token, form_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def sanitize_text(value: str) -> str:
    return bleach.clean((value or "").strip(), tags=[], attributes={}, strip=True)


def sanitize_optional_text(value: str, max_length: int) -> str:
    cleaned = sanitize_text(value)
    if len(cleaned) > max_length:
        raise HTTPException(status_code=400, detail=f"Field exceeds the {max_length} character limit")
    return cleaned


def sanitize_required_text(value: str, field_name: str, max_length: int) -> str:
    cleaned = sanitize_optional_text(value, max_length)
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


def normalize_package_id(value: str) -> str:
    candidate = sanitize_text(value).lower()
    if not PACKAGE_ID_PATTERN.fullmatch(candidate):
        raise HTTPException(
            status_code=400,
            detail="package_id must be 3-64 characters and use only lowercase letters, numbers, hyphens, or underscores",
        )
    return candidate


def parse_list_field(raw_value: str, field_name: str, max_items: int = 16, max_length: int = 160) -> list[str]:
    parsed_items: list[str] = []
    for line in (raw_value or "").splitlines():
        cleaned_line = sanitize_optional_text(line.strip().lstrip("- ").strip(), max_length)
        if cleaned_line:
            parsed_items.append(cleaned_line)
    if len(parsed_items) > max_items:
        raise HTTPException(status_code=400, detail=f"{field_name} can contain at most {max_items} items")
    return parsed_items


def parse_facts(raw_value: str, max_items: int = 8, max_length: int = 48) -> list[str]:
    parsed_items: list[str] = []
    for item in (raw_value or "").replace("\n", ",").split(","):
        cleaned_item = sanitize_optional_text(item, max_length)
        if cleaned_item:
            parsed_items.append(cleaned_item)
    if len(parsed_items) > max_items:
        raise HTTPException(status_code=400, detail=f"facts can contain at most {max_items} items")
    return parsed_items


def parse_itinerary(raw_value: str) -> list[dict[str, object]]:
    parsed_itinerary: list[dict[str, object]] = []
    current_day: dict[str, object] | None = None

    for line in (raw_value or "").splitlines():
        cleaned_line = sanitize_text(line)
        if not cleaned_line:
            continue

        if cleaned_line.lower().startswith("day"):
            if len(parsed_itinerary) >= 20:
                raise HTTPException(status_code=400, detail="itinerary can contain at most 20 days")
            parts = cleaned_line.split(":", 1)
            day_label = sanitize_required_text(parts[0], "itinerary day", 32)
            day_title = sanitize_optional_text(parts[1] if len(parts) > 1 else "", 120)
            current_day = {
                "day": day_label,
                "title": day_title,
                "items": [],
            }
            parsed_itinerary.append(current_day)
            continue

        if cleaned_line.startswith("-") and current_day is not None:
            item = sanitize_required_text(cleaned_line[1:], "itinerary item", 180)
            items = current_day["items"]
            if len(items) >= 12:
                raise HTTPException(status_code=400, detail="each itinerary day can contain at most 12 items")
            items.append(item)

    return parsed_itinerary


def build_cloudinary_public_id(package_id: str, filename: str) -> str:
    filename_root = os.path.splitext(filename or "")[0]
    candidate = sanitize_text(package_id or filename_root or "package-image").lower()
    slug = re.sub(r"[^a-z0-9_-]+", "-", candidate).strip("-") or "package-image"
    return f"{slug}-{secrets.token_hex(4)}"


def get_cloudinary_upload_config() -> dict[str, str]:
    config = cloudinary.config()
    cloud_name = getattr(config, "cloud_name", None) or os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = getattr(config, "api_key", None) or os.environ.get("CLOUDINARY_API_KEY")
    api_secret = getattr(config, "api_secret", None) or os.environ.get("CLOUDINARY_API_SECRET")

    if not cloud_name or not api_key or not api_secret:
        raise HTTPException(status_code=503, detail="Cloudinary uploads are not configured")

    return {
        "cloud_name": cloud_name,
        "api_key": api_key,
        "api_secret": api_secret,
        "folder": CLOUDINARY_UPLOAD_FOLDER,
    }


def is_allowed_cloudinary_url(raw_value: str) -> bool:
    parsed = urlparse(raw_value)
    if parsed.scheme != "https" or parsed.netloc != "res.cloudinary.com":
        return False

    cloud_name = get_cloudinary_upload_config()["cloud_name"]
    path = parsed.path
    prefix = f"/{cloud_name}/image/upload/"
    if not path.startswith(prefix):
        return False

    return f"/{CLOUDINARY_UPLOAD_FOLDER}/" in path or path.endswith(f"/{CLOUDINARY_UPLOAD_FOLDER}")


def validate_image_reference(card_image: str) -> str:
    image_value = (card_image or "").strip()
    if not image_value:
        return ""

    if image_value.startswith("./statics/"):
        return image_value[1:]

    if image_value.startswith("/statics/"):
        return image_value

    if image_value.startswith("data:"):
        raise HTTPException(status_code=400, detail="Inline image payloads are not allowed")

    if not is_allowed_cloudinary_url(image_value):
        raise HTTPException(status_code=400, detail="card_image must be a local asset or a valid Cloudinary URL")

    return image_value


def build_package_payload(
    package_id: str,
    title: str,
    price: str,
    badge: str,
    summary: str,
    eyebrow: str,
    itinerary: str,
    inclusions: str,
    exclusions: str,
    carry: str,
    highlights: str,
    facts: str,
) -> dict[str, object]:
    return {
        "package_id": normalize_package_id(package_id),
        "title": sanitize_required_text(title, "title", 120),
        "price": sanitize_required_text(price, "price", 40),
        "badge": sanitize_required_text(badge, "badge", 40),
        "summary": sanitize_required_text(summary, "summary", 600),
        "eyebrow": sanitize_required_text(eyebrow, "eyebrow", 60),
        "facts": parse_facts(facts),
        "itinerary": parse_itinerary(itinerary),
        "highlights": parse_list_field(highlights, "highlights"),
        "inclusions": parse_list_field(inclusions, "inclusions"),
        "exclusions": parse_list_field(exclusions, "exclusions"),
        "carry": parse_list_field(carry, "carry"),
    }


def normalize_package_media(pkg: dict) -> dict:
    package_copy = dict(pkg)
    for key in ("card_image", "image"):
        value = package_copy.get(key, "")
        if isinstance(value, str) and value.startswith("./"):
            package_copy[key] = value[1:]
    return package_copy


async def log_admin_event(
    request: Request,
    action: str,
    success: bool,
    actor: str | None = None,
    target_package_id: str | None = None,
    reason: str | None = None,
) -> None:
    expires_at = now_utc() + timedelta(days=AUDIT_LOG_RETENTION_DAYS)
    document = {
        "created_at": now_utc(),
        "expires_at": expires_at,
        "actor": actor,
        "action": action,
        "target_package_id": target_package_id,
        "ip": get_client_ip(request),
        "user_agent_hash": hash_user_agent(request),
        "success": success,
        "reason": sanitize_optional_text(reason or "", 240) if reason else None,
        "path": request.url.path,
    }
    try:
        await audit_log_collection.insert_one(document)
    except Exception:
        return


async def get_login_retry_after_seconds(client_ip: str, username: str) -> int:
    key = f"login:{username.lower()}:{client_ip}"
    attempt = await login_attempts_collection.find_one({"key": key})
    if not attempt:
        return 0

    blocked_until = coerce_utc_datetime(attempt.get("blocked_until"))
    if blocked_until and blocked_until > now_utc():
        return max(int((blocked_until - now_utc()).total_seconds()), 1)

    return 0


async def register_failed_login(client_ip: str, username: str) -> None:
    key = f"login:{username.lower()}:{client_ip}"
    now = now_utc()
    existing = await login_attempts_collection.find_one({"key": key})
    existing_window_expires_at = coerce_utc_datetime(existing.get("window_expires_at")) if existing else None

    if not existing or not existing_window_expires_at or existing_window_expires_at <= now:
        count = 1
    else:
        count = int(existing.get("count", 0)) + 1

    window_expires_at = now + timedelta(seconds=LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    blocked_until = window_expires_at if count >= LOGIN_RATE_LIMIT_MAX_FAILURES else None

    await login_attempts_collection.update_one(
        {"key": key},
        {
            "$set": {
                "count": count,
                "last_failure_at": now,
                "window_expires_at": window_expires_at,
                "blocked_until": blocked_until,
            },
            "$setOnInsert": {"key": key, "created_at": now},
        },
        upsert=True,
    )


async def clear_failed_logins(client_ip: str, username: str) -> None:
    key = f"login:{username.lower()}:{client_ip}"
    await login_attempts_collection.delete_one({"key": key})


def verify_admin_password(raw_password: str) -> bool:
    if ADMIN_PASSWORD_HASH:
        try:
            return PASSWORD_HASHER.verify(ADMIN_PASSWORD_HASH, raw_password)
        except (InvalidHashError, VerificationError, VerifyMismatchError):
            return False
    return secrets.compare_digest(raw_password, LEGACY_ADMIN_PASS)


def csp_value(nonce: str) -> str:
    frame_src = "https://lookerstudio.google.com" if LOOKER_STUDIO_EMBED_URL else "'none'"
    return "; ".join(
        [
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}'",
            "style-src 'self'",
            "img-src 'self' data: https://res.cloudinary.com",
            "font-src 'self'",
            "connect-src 'self' https://api.cloudinary.com",
            f"frame-src {frame_src}",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests",
        ]
    )


async def ensure_indexes() -> None:
    await packages_collection.create_index("package_id", unique=True, name="unique_package_id")
    await sessions_collection.create_index("session_id_hash", unique=True, name="unique_session_id_hash")
    await sessions_collection.create_index("expires_at", expireAfterSeconds=0)
    await login_attempts_collection.create_index("key", unique=True, name="unique_rate_limit_key")
    await login_attempts_collection.create_index("window_expires_at", expireAfterSeconds=0)
    await audit_log_collection.create_index("expires_at", expireAfterSeconds=0)


@asynccontextmanager
async def app_lifespan(application: FastAPI):
    await ensure_indexes()
    yield


app = FastAPI(lifespan=app_lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.mount("/statics", StaticFiles(directory=os.path.join(BASE_DIR, "statics")), name="statics")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    if GOOGLE_SITE_VERIFICATION_HTML_FILENAME and request.url.path == f"/{GOOGLE_SITE_VERIFICATION_HTML_FILENAME}":
        return HTMLResponse(content=GOOGLE_SITE_VERIFICATION_HTML_CONTENT)

    request.state.csp_nonce = secrets.token_urlsafe(16)
    response = await call_next(request)

    path = request.url.path
    is_auth_or_admin = path == "/login" or path.startswith("/admin")

    response.headers["Content-Security-Policy"] = csp_value(request.state.csp_nonce)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), browsing-topics=(), interest-cohort=()"
    )
    response.headers["X-Frame-Options"] = "DENY"

    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    if is_auth_or_admin:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"

    if is_auth_or_admin or response.status_code >= 400:
        response.headers["X-Robots-Tag"] = "noindex, nofollow"

    return response


@app.get("/robots.txt", response_class=FileResponse)
async def get_robots_txt():
    return FileResponse(os.path.join(BASE_DIR, "statics", "robots.txt"), media_type="text/plain")


@app.get("/sitemap.xml", response_class=FileResponse)
async def get_sitemap_xml():
    return FileResponse(os.path.join(BASE_DIR, "statics", "sitemap.xml"), media_type="application/xml")


@app.get("/llms.txt", response_class=FileResponse)
async def get_llms_txt():
    return FileResponse(os.path.join(BASE_DIR, "statics", "llms.txt"), media_type="text/plain")


@app.get("/humans.txt", response_class=FileResponse)
async def get_humans_txt():
    return FileResponse(os.path.join(BASE_DIR, "statics", "humans.txt"), media_type="text/plain")


@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "statics", "assets", "favicon.ico"), media_type="image/x-icon")


async def get_current_admin(request: Request) -> str:
    session_id = request.cookies.get(AUTH_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    session = await sessions_collection.find_one(
        {
            "session_id_hash": hash_value(session_id),
            "username": ADMIN_USER,
            "revoked_at": None,
        }
    )
    expires_at = coerce_utc_datetime(session.get("expires_at")) if session else None
    if not session or not expires_at or expires_at <= now_utc():
        raise HTTPException(status_code=303, headers={"Location": "/login"})

    request.state.admin_session = session
    return ADMIN_USER


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code in [301, 302, 303, 307, 308]:
        headers = dict(exc.headers) if exc.headers else {}
        return RedirectResponse(
            url=headers.get("Location") or headers.get("location") or "/",
            status_code=exc.status_code,
        )

    error_message = exc.detail
    if exc.status_code == 404:
        error_message = "The travel destination you are looking for has vanished from our maps."
    elif exc.status_code in {401, 403}:
        error_message = "You lack the required passes to access this sector."

    return render_template(
        request=request,
        name="error.html",
        context={"error_code": exc.status_code, "error_message": error_message},
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def custom_500_exception_handler(request: Request, exc: Exception):
    return render_template(
        request=request,
        name="error.html",
        context={
            "error_code": 500,
            "error_message": "Our infrastructure encountered a rough mountain pass. The technical team has been notified!",
        },
        status_code=500,
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    packages = [normalize_package_media(pkg) async for pkg in packages_collection.find({}).limit(100)]
    return render_template(request=request, name="index.html", context={"packages": packages})


@app.get("/packages", response_class=HTMLResponse)
@app.get("/packages/", response_class=HTMLResponse)
async def read_packages(request: Request):
    packages = [normalize_package_media(pkg) async for pkg in packages_collection.find({}).limit(100)]
    return render_template(request=request, name="packages.html", context={"packages": packages})


@app.get("/api/packages", response_class=JSONResponse)
async def api_packages():
    packages = [normalize_package_media(pkg) async for pkg in packages_collection.find({}, {"_id": 0}).limit(100)]
    packages_dict = {pkg["package_id"]: pkg for pkg in packages}
    return JSONResponse(content=packages_dict)


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return render_template(request=request, name="login.html", include_csrf=True)


@app.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(""),
):
    validate_csrf(request, csrf_token)
    client_ip = get_client_ip(request)
    normalized_username = sanitize_text(username)
    retry_after = await get_login_retry_after_seconds(client_ip, normalized_username)
    if retry_after:
        wait_minutes = max((retry_after + 59) // 60, 1)
        await log_admin_event(
            request,
            action="login_rate_limited",
            success=False,
            actor=normalized_username,
            reason=f"retry_after={retry_after}",
        )
        return render_template(
            request=request,
            name="login.html",
            context={"error": f"Too many failed login attempts. Try again in {wait_minutes} minute(s)."},
            status_code=429,
            include_csrf=True,
        )

    if normalized_username == ADMIN_USER and verify_admin_password(password):
        await clear_failed_logins(client_ip, normalized_username)
        session_id = secrets.token_urlsafe(32)
        expires_at = now_utc() + timedelta(seconds=SESSION_TTL_SECONDS)
        await sessions_collection.insert_one(
            {
                "session_id_hash": hash_value(session_id),
                "username": ADMIN_USER,
                "created_at": now_utc(),
                "expires_at": expires_at,
                "revoked_at": None,
                "ip": client_ip,
                "user_agent_hash": hash_user_agent(request),
            }
        )
        await log_admin_event(request, action="login_success", success=True, actor=ADMIN_USER)
        response = RedirectResponse(url="/admin", status_code=303)
        set_session_cookie(response, session_id)
        return response

    await register_failed_login(client_ip, normalized_username)
    await log_admin_event(request, action="login_failure", success=False, actor=normalized_username)
    return render_template(
        request=request,
        name="login.html",
        context={"error": "Invalid username or password"},
        status_code=401,
        include_csrf=True,
    )


@app.post("/admin/logout")
async def logout(
    request: Request,
    csrf_token: str = Form(""),
    admin_user: str = Depends(get_current_admin),
):
    validate_csrf(request, csrf_token)
    session_id = request.cookies.get(AUTH_COOKIE_NAME)
    if session_id:
        await sessions_collection.update_one(
            {"session_id_hash": hash_value(session_id)},
            {"$set": {"revoked_at": now_utc()}},
        )
    await log_admin_event(request, action="logout", success=True, actor=admin_user)
    response = RedirectResponse(url="/login", status_code=303)
    clear_session_cookie(response)
    clear_csrf_cookie(response)
    return response


@app.get("/admin", response_class=HTMLResponse)
async def read_admin(request: Request, admin_user: str = Depends(get_current_admin)):
    packages = [normalize_package_media(pkg) async for pkg in packages_collection.find({}).limit(100)]
    return render_template(
        request=request,
        name="admin.html",
        context={"packages": packages},
        include_csrf=True,
    )


@app.post("/admin/cloudinary-signature")
async def admin_cloudinary_signature(
    request: Request,
    admin_user: str = Depends(get_current_admin),
):
    validate_csrf(request, request.headers.get("x-csrf-token", ""))
    payload = await request.json()
    normalized_package_id = normalize_package_id(str(payload.get("package_id", "") or "package-image"))

    cloudinary_config = get_cloudinary_upload_config()
    timestamp = int(time.time())
    public_id = build_cloudinary_public_id(
        package_id=normalized_package_id,
        filename=str(payload.get("filename", "")),
    )

    params_to_sign = {
        "allowed_formats": ",".join(sorted(mime_type.split("/")[1] for mime_type in ALLOWED_IMAGE_MIME_TYPES)),
        "folder": cloudinary_config["folder"],
        "max_file_size": MAX_IMAGE_UPLOAD_BYTES,
        "overwrite": "false",
        "public_id": public_id,
        "timestamp": timestamp,
    }
    signature = cloudinary.utils.api_sign_request(params_to_sign, cloudinary_config["api_secret"])
    await log_admin_event(
        request,
        action="cloudinary_signature",
        success=True,
        actor=admin_user,
        target_package_id=normalized_package_id,
    )

    return JSONResponse(
        content={
            "api_key": cloudinary_config["api_key"],
            "cloud_name": cloudinary_config["cloud_name"],
            "folder": cloudinary_config["folder"],
            "public_id": public_id,
            "signature": signature,
            "timestamp": timestamp,
            "upload_url": f"https://api.cloudinary.com/v1_1/{cloudinary_config['cloud_name']}/image/upload",
            "allowed_formats": ["gif", "jpeg", "jpg", "png", "webp"],
            "max_file_size": MAX_IMAGE_UPLOAD_BYTES,
            "overwrite": False,
        }
    )


@app.post("/admin/add")
async def admin_add_package(
    request: Request,
    package_id: str = Form(...),
    title: str = Form(...),
    price: str = Form(...),
    badge: str = Form(...),
    summary: str = Form(...),
    eyebrow: str = Form(...),
    card_image: str = Form(...),
    itinerary: str = Form(""),
    inclusions: str = Form(""),
    exclusions: str = Form(""),
    carry: str = Form(""),
    highlights: str = Form(""),
    facts: str = Form(""),
    csrf_token: str = Form(""),
    admin_user: str = Depends(get_current_admin),
):
    validate_csrf(request, csrf_token)
    new_package = build_package_payload(
        package_id=package_id,
        title=title,
        price=price,
        badge=badge,
        summary=summary,
        eyebrow=eyebrow,
        itinerary=itinerary,
        inclusions=inclusions,
        exclusions=exclusions,
        carry=carry,
        highlights=highlights,
        facts=facts,
    )
    validated_image = validate_image_reference(card_image)
    if not validated_image:
        raise HTTPException(status_code=400, detail="card_image is required")

    new_package["card_image"] = validated_image
    new_package["image"] = validated_image

    try:
        await packages_collection.insert_one(new_package)
    except DuplicateKeyError:
        await log_admin_event(
            request,
            action="package_create",
            success=False,
            actor=admin_user,
            target_package_id=new_package["package_id"],
            reason="duplicate package_id",
        )
        raise HTTPException(status_code=400, detail="A package with that package_id already exists")

    await log_admin_event(
        request,
        action="package_create",
        success=True,
        actor=admin_user,
        target_package_id=new_package["package_id"],
    )
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/delete/{pkg_id}")
async def admin_delete_package(
    request: Request,
    pkg_id: str,
    csrf_token: str = Form(""),
    admin_user: str = Depends(get_current_admin),
):
    validate_csrf(request, csrf_token)
    normalized_pkg_id = normalize_package_id(pkg_id)
    await packages_collection.delete_one({"package_id": normalized_pkg_id})
    await log_admin_event(
        request,
        action="package_delete",
        success=True,
        actor=admin_user,
        target_package_id=normalized_pkg_id,
    )
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/edit/{package_id}", response_class=HTMLResponse)
async def admin_edit_package_view(
    request: Request,
    package_id: str,
    admin_user: str = Depends(get_current_admin),
):
    normalized_package_id = normalize_package_id(package_id)
    pkg = await packages_collection.find_one({"package_id": normalized_package_id})
    if not pkg:
        raise HTTPException(status_code=404, detail=f"The package '{normalized_package_id}' could not be located.")

    pkg = normalize_package_media(pkg)
    itinerary_text_lines: list[str] = []
    for day in pkg.get("itinerary", []):
        itinerary_text_lines.append(f"{day.get('day')}: {day.get('title')}".strip())
        for item in day.get("items", []):
            itinerary_text_lines.append(f"- {item}")

    pkg["itinerary_text"] = "\n".join(itinerary_text_lines).strip()
    pkg["inclusions_text"] = "\n".join([f"- {item}" for item in pkg.get("inclusions", [])])
    pkg["exclusions_text"] = "\n".join([f"- {item}" for item in pkg.get("exclusions", [])])
    pkg["carry_text"] = "\n".join([f"- {item}" for item in pkg.get("carry", [])])
    pkg["highlights_text"] = "\n".join([f"- {item}" for item in pkg.get("highlights", [])])
    pkg["facts_text"] = ", ".join(pkg.get("facts", []))

    return render_template(
        request=request,
        name="edit_package.html",
        context={"pkg": pkg},
        include_csrf=True,
    )


@app.post("/admin/edit/{update_package_id}")
async def admin_edit_package_post(
    request: Request,
    update_package_id: str,
    package_id: str = Form(...),
    title: str = Form(...),
    price: str = Form(...),
    badge: str = Form(...),
    summary: str = Form(...),
    eyebrow: str = Form(...),
    card_image: str = Form(""),
    itinerary: str = Form(""),
    inclusions: str = Form(""),
    exclusions: str = Form(""),
    carry: str = Form(""),
    highlights: str = Form(""),
    facts: str = Form(""),
    csrf_token: str = Form(""),
    admin_user: str = Depends(get_current_admin),
):
    validate_csrf(request, csrf_token)
    normalized_update_package_id = normalize_package_id(update_package_id)
    update_fields = build_package_payload(
        package_id=package_id,
        title=title,
        price=price,
        badge=badge,
        summary=summary,
        eyebrow=eyebrow,
        itinerary=itinerary,
        inclusions=inclusions,
        exclusions=exclusions,
        carry=carry,
        highlights=highlights,
        facts=facts,
    )

    if card_image:
        validated_image = validate_image_reference(card_image)
        update_fields["card_image"] = validated_image
        update_fields["image"] = validated_image

    try:
        result = await packages_collection.update_one(
            {"package_id": normalized_update_package_id},
            {"$set": update_fields},
        )
    except DuplicateKeyError:
        await log_admin_event(
            request,
            action="package_update",
            success=False,
            actor=admin_user,
            target_package_id=update_fields["package_id"],
            reason="duplicate package_id",
        )
        raise HTTPException(status_code=400, detail="A package with that package_id already exists")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Package not found")

    await log_admin_event(
        request,
        action="package_update",
        success=True,
        actor=admin_user,
        target_package_id=update_fields["package_id"],
    )
    return RedirectResponse(url="/admin", status_code=303)
