from fastapi import FastAPI, Request, Form, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import mimetypes
from dotenv import load_dotenv

# Securely inject missing mimetypes for Vercel's serverless environment
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")

# Load secret environment variables
load_dotenv()
import jwt
from datetime import datetime, timedelta, timezone
import cloudinary
import cloudinary.uploader
if os.environ.get("CLOUDINARY_URL"):
    cloudinary.config(url=os.environ.get("CLOUDINARY_URL"))

app = FastAPI()

# Add GZip Middleware for robust server-side compression
app.add_middleware(GZipMiddleware, minimum_size=500)

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment (.env)")
import certifi
client = AsyncIOMotorClient(
    MONGO_URI, tlsCAFile=certifi.where()
)
db = client.ghoomne_chalo
packages_collection = db.packages

from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

# Define base directory globally to work in Vercel functions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount the statics directory so that CSS, JS, and assets can be served
app.mount("/statics", StaticFiles(directory=os.path.join(BASE_DIR, "statics")), name="statics")

# --- SEO AND BOT ENDPOINTS ---
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

# Set up templates directory
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- CUSTOM ERROR HANDLERS ---
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Pass along redirects seamlessly
    if exc.status_code in [301, 302, 303, 307, 308]:
        headers = dict(exc.headers) if exc.headers else {}
        return RedirectResponse(
            url=headers.get("Location") or headers.get("location") or "/", 
            status_code=exc.status_code
        )
        
    error_message = exc.detail
    if exc.status_code == 404:
        error_message = "The travel destination you are looking for has vanished from our maps."
    elif exc.status_code == 401 or exc.status_code == 403:
        error_message = "You lack the required passes to access this sector."
        
    return templates.TemplateResponse(
        request=request, 
        name="error.html", 
        context={"error_code": exc.status_code, "error_message": error_message},
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def custom_500_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request=request, 
        name="error.html", 
        context={"error_code": 500, "error_message": "Our infrastructure encounted a rough mountain pass. The technical team has been notified!"},
        status_code=500
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Fetch packages from the database to render dynamically
    packages_cursor = packages_collection.find({})
    packages = await packages_cursor.to_list(length=100)
    
    # Serve the index.html from the templates folder with dynamic packages
    return templates.TemplateResponse(request=request, name="index.html", context={"packages": packages})

@app.get("/packages", response_class=HTMLResponse)
@app.get("/packages/", response_class=HTMLResponse)
async def read_packages(request: Request):
    # Fetch packages from the database to render dynamically
    packages_cursor = packages_collection.find({})
    packages = await packages_cursor.to_list(length=100)
    for pkg in packages:
        if pkg.get("card_image", "").startswith("./"):
            pkg["card_image"] = pkg["card_image"][1:]
        if pkg.get("image", "").startswith("./"):
            pkg["image"] = pkg["image"][1:]
    
    # Serve the packages.html from the templates folder
    return templates.TemplateResponse(request=request, name="packages.html", context={"packages": packages})

# Add an endpoint for the JS script to fetch full package details for the modal
@app.get("/api/packages", response_class=HTMLResponse)
async def api_packages():
    packages_cursor = packages_collection.find({}, {"_id": 0})
    packages = await packages_cursor.to_list(length=100)
    for pkg in packages:
        if pkg.get("card_image", "").startswith("./"):
            pkg["card_image"] = pkg["card_image"][1:]
        if pkg.get("image", "").startswith("./"):
            pkg["image"] = pkg["image"][1:]
    # converting list of dicts to a dict based on package_id to match JS format
    packages_dict = {pkg["package_id"]: pkg for pkg in packages}
    from fastapi.responses import JSONResponse
    return JSONResponse(content=packages_dict)

# --- AUTH & ADMIN VARIABLES ---
SECRET_KEY = os.environ.get("JWT_SECRET", "ghoomne_super_secret_key_123!")
ALGORITHM = "HS256"
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "ghoomne123")

async def get_current_admin(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != ADMIN_USER:
            raise HTTPException(status_code=303, headers={"Location": "/login"})
    except jwt.PyJWTError:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return username

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        expiration = datetime.now(timezone.utc) + timedelta(days=7)
        token = jwt.encode({"sub": username, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_token", value=token, httponly=True, max_age=604800, samesite="lax")
        return response
    return templates.TemplateResponse(request=request, name="login.html", context={"error": "Invalid username or password"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("admin_token")
    return response

# --- ADMIN PANEL ---
@app.get("/admin", response_class=HTMLResponse)
async def read_admin(request: Request, admin_user: str = Depends(get_current_admin)):
    packages_cursor = packages_collection.find({})
    packages = await packages_cursor.to_list(length=100)
    return templates.TemplateResponse(request=request, name="admin.html", context={"packages": packages})

@app.post("/admin/add")
async def admin_add_package(
    package_id: str = Form(...),
    title: str = Form(...),
    price: str = Form(...),
    badge: str = Form(...) ,
    summary: str = Form(...),
    eyebrow: str = Form(...),
    card_image: str = Form(...),
    itinerary: str = Form(""),
    inclusions: str = Form(""),
    exclusions: str = Form(""),
    carry: str = Form(""),
    highlights: str = Form(""),
    facts: str = Form(""),
    admin_user: str = Depends(get_current_admin)
):
    parsed_facts = [f.strip() for f in facts.replace("\n", ",").split(",") if f.strip()] if facts else []
    parsed_inclusions = [i.strip().lstrip("- ") for i in inclusions.split("\n") if i.strip()] if inclusions else []
    parsed_exclusions = [e.strip().lstrip("- ") for e in exclusions.split("\n") if e.strip()] if exclusions else []
    parsed_carry = [c.strip().lstrip("- ") for c in carry.split("\n") if c.strip()] if carry else []
    parsed_highlights = [h.strip().lstrip("- ") for h in highlights.split("\n") if h.strip()] if highlights else []

    parsed_itinerary = []
    if itinerary:
        current_day = None
        for line in itinerary.split('\n'):
            line = line.strip()
            if not line: continue
            if line.lower().startswith('day'):
                parts = line.split(':', 1)
                current_day = {"day": parts[0].strip(), "title": parts[1].strip() if len(parts)>1 else "", "items": []}
                parsed_itinerary.append(current_day)
            elif line.startswith('-') and current_day is not None:
                current_day["items"].append(line[1:].strip())

    if card_image.startswith("data:image/"):
        upload_result = cloudinary.uploader.upload(card_image)
        card_image = upload_result.get("secure_url")

    new_package = {
        "package_id": package_id,
        "title": title,
        "price": price,
        "badge": badge,
        "summary": summary,
        "eyebrow": eyebrow,
        "card_image": card_image,
        "image": card_image,  # Same as card image for simplicity
        "facts": parsed_facts,
        "itinerary": parsed_itinerary,
        "highlights": parsed_highlights,
        "inclusions": parsed_inclusions,
        "exclusions": parsed_exclusions,
        "carry": parsed_carry
    }
    
    await packages_collection.insert_one(new_package)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/delete/{pkg_id}")
async def admin_delete_package(pkg_id: str, admin_user: str = Depends(get_current_admin)):
    await packages_collection.delete_one({"package_id": pkg_id})
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/admin/edit/{package_id}", response_class=HTMLResponse)
async def admin_edit_package_view(request: Request, package_id: str, admin_user: str = Depends(get_current_admin)):
    pkg = await packages_collection.find_one({"package_id": package_id})
    if not pkg:
        raise HTTPException(status_code=404, detail=f"The package '{package_id}' could not be located in our database.")
    
    # Format the itinerary back to text
    it_text = ""
    for day in pkg.get("itinerary", []):
        it_text += f"Day {day.get('day').replace('Day ', '')}: {day.get('title')}\n"
        for item in day.get("items", []):
            it_text += f"- {item}\n"
            
    # Add formatted text fields to pkg object specifically for the edit form
    pkg["itinerary_text"] = it_text.strip()
    pkg["inclusions_text"] = "\n".join(["- " + i for i in pkg.get("inclusions", [])])
    pkg["exclusions_text"] = "\n".join(["- " + e for e in pkg.get("exclusions", [])])
    pkg["carry_text"] = "\n".join(["- " + c for c in pkg.get("carry", [])])
    pkg["highlights_text"] = "\n".join(["- " + h for h in pkg.get("highlights", [])])
    pkg["facts_text"] = ", ".join(pkg.get("facts", []))
    
    return templates.TemplateResponse(request=request, name="edit_package.html", context={"pkg": pkg})

@app.post("/admin/edit/{update_package_id}")
async def admin_edit_package_post(
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
    admin_user: str = Depends(get_current_admin)
):
    parsed_facts = [f.strip() for f in facts.replace("\n", ",").split(",") if f.strip()] if facts else []
    parsed_inclusions = [i.strip().lstrip("- ") for i in inclusions.split("\n") if i.strip()] if inclusions else []
    parsed_exclusions = [e.strip().lstrip("- ") for e in exclusions.split("\n") if e.strip()] if exclusions else []
    parsed_carry = [c.strip().lstrip("- ") for c in carry.split("\n") if c.strip()] if carry else []
    parsed_highlights = [h.strip().lstrip("- ") for h in highlights.split("\n") if h.strip()] if highlights else []

    parsed_itinerary = []
    if itinerary:
        current_day = None
        for line in itinerary.split('\n'):
            line = line.strip()
            if not line: continue
            if line.lower().startswith('day'):
                parts = line.split(':', 1)
                current_day = {"day": parts[0].strip(), "title": parts[1].strip() if len(parts)>1 else "", "items": []}
                parsed_itinerary.append(current_day)
            elif line.startswith('-') and current_day is not None:
                current_day["items"].append(line[1:].strip())

    if card_image and card_image.startswith("data:image/"):
        upload_result = cloudinary.uploader.upload(card_image)
        card_image = upload_result.get("secure_url", "")

    update_fields = {
        "package_id": package_id,
        "title": title,
        "price": price,
        "badge": badge,
        "summary": summary,
        "eyebrow": eyebrow,
        "facts": parsed_facts,
        "itinerary": parsed_itinerary,
        "highlights": parsed_highlights,
        "inclusions": parsed_inclusions,
        "exclusions": parsed_exclusions,
        "carry": parsed_carry
    }
    if card_image:
        update_fields["card_image"] = card_image
        update_fields["image"] = card_image

    await packages_collection.update_one(
        {"package_id": update_package_id},
        {"$set": update_fields}
    )
    return RedirectResponse(url="/admin", status_code=303)
