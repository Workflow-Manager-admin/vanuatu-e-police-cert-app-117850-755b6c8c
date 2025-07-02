from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid
import os
from enum import Enum

app = FastAPI(
    title="Electronic Police Certificate System API",
    description="API for managing Vanuatu Police Force's Electronic Police Certificate requests, processing, and administration",
    version="1.0.0",
    openapi_tags=[
        {"name": "Auth", "description": "User registration and authentication"},
        {"name": "Application", "description": "Certificate application submission and status tracking"},
        {"name": "Certificate", "description": "Management and download of police certificates"},
        {"name": "Admin", "description": "Administrative operations for application review and processing"},
        {"name": "Health", "description": "System health check"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- DATABASE MOCKS (Replace with real db access in production) -----
MOCK_USERS = {}
MOCK_CERT_APPS = {}
MOCK_CERT_FILES = {}
MOCK_TOKENS = {}

# ----- UTILITY FUNCTIONS -----
def fake_hash_password(password: str) -> str:
    return "hashed_" + password

def fake_verify_password(raw: str, hashed: str) -> bool:
    return fake_hash_password(raw) == hashed

def fake_create_access_token(user_id: str) -> str:
    # In production, use JWT & secret key with exp
    token = str(uuid.uuid4())
    MOCK_TOKENS[token] = user_id
    return token

def fake_decode_token(token: str) -> Optional[str]:
    return MOCK_TOKENS.get(token)

# ----- AUTH MODELS -----
class UserRegistration(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    full_name: str = Field(..., description="Applicant's full name")
    phone: Optional[str] = Field(None, description="Contact phone number")

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfo(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_admin: bool
    status: str

# ----- EPC APPLICATION MODELS -----
class EPCApplicationRequest(BaseModel):
    purpose: str = Field(..., description="Purpose for requesting the certificate")
    passport_number: str = Field(..., description="Passport number")
    country_of_application: str = Field(..., description="Country where certificate will be used")
    address: str = Field(..., description="Applicant's current address")

class EPCApplicationStatus(str, Enum):
    """Status for Electronic Police Certificate application."""
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ISSUED = "ISSUED"

class EPCApplicationSummary(BaseModel):
    id: str
    user_id: str
    date_submitted: datetime
    purpose: str
    status: EPCApplicationStatus
    last_updated: datetime

    class Config:
        use_enum_values = True

class EPCApplicationDetail(EPCApplicationSummary):
    passport_number: str
    country_of_application: str
    address: str
    admin_notes: Optional[str] = None

class EPCAdminAction(BaseModel):
    status: EPCApplicationStatus
    admin_notes: Optional[str] = None

# ----- SECURITY DEPENDENCIES -----
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInfo:
    """
    Security dependency for extracting current user from token.
    """
    user_id = fake_decode_token(token)
    user = MOCK_USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

# PUBLIC_INTERFACE
def get_admin_user(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    """Security dependency: checks for admin user rights."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not an admin user")
    return user


# ----- AUTH ROUTES -----
@app.post("/auth/register", response_model=TokenResponse, tags=["Auth"], summary="Register a new user")
# PUBLIC_INTERFACE
def register_user(reg_data: UserRegistration):
    """
    Registers a new user given registration details.
    """
    if any(u.email == reg_data.email for u in MOCK_USERS.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    user = UserInfo(
        id=user_id,
        email=reg_data.email,
        full_name=reg_data.full_name,
        is_admin=False,
        status="active"
    )
    MOCK_USERS[user_id] = user
    # Store mock password for now
    setattr(user, "password_hash", fake_hash_password(reg_data.password))
    return TokenResponse(access_token=fake_create_access_token(user_id=user_id))


@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"], summary="Login user (returns access token)")
# PUBLIC_INTERFACE
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates user and returns an access token.
    """
    # Only search users
    for u in MOCK_USERS.values():
        if u.email == form_data.username:
            if fake_verify_password(form_data.password, getattr(u, "password_hash", "")):
                return TokenResponse(access_token=fake_create_access_token(user_id=u.id))
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/auth/me", response_model=UserInfo, tags=["Auth"], summary="Get current user's info")
# PUBLIC_INTERFACE
def get_me(user: UserInfo = Depends(get_current_user)):
    """
    Returns the currently authenticated user's info.
    """
    return user

# ----- EPC APPLICATION ROUTES -----
@app.post("/epc/application", response_model=EPCApplicationSummary, tags=["Application"], summary="Submit police certificate application")
# PUBLIC_INTERFACE
def submit_epc_application(
    app_data: EPCApplicationRequest,
    user: UserInfo = Depends(get_current_user)
):
    """
    Submits a new electronic police certificate application.
    """
    app_id = str(uuid.uuid4())
    now = datetime.utcnow()
    summary = EPCApplicationSummary(
        id=app_id,
        user_id=user.id,
        date_submitted=now,
        purpose=app_data.purpose,
        status=EPCApplicationStatus.SUBMITTED,
        last_updated=now,
    )
    MOCK_CERT_APPS[app_id] = {
        "summary": summary,
        "detail": EPCApplicationDetail(
            **summary.dict(),
            passport_number=app_data.passport_number,
            country_of_application=app_data.country_of_application,
            address=app_data.address,
            admin_notes=None
        ),
        "certificate_file": None
    }
    return summary

@app.get("/epc/application", response_model=List[EPCApplicationSummary], tags=["Application"], summary="List user's certificate applications")
# PUBLIC_INTERFACE
def list_user_epc_applications(user: UserInfo = Depends(get_current_user)):
    """
    Lists all electronic police certificate applications for the current user.
    """
    return [
        app["summary"]
        for app in MOCK_CERT_APPS.values()
        if app["summary"].user_id == user.id
    ]

@app.get("/epc/application/{app_id}", response_model=EPCApplicationDetail, tags=["Application"], summary="Get certificate application details")
# PUBLIC_INTERFACE
def get_epc_application_detail(
    app_id: str, user: UserInfo = Depends(get_current_user)
):
    """
    Returns the details of a police certificate application.
    """
    app = MOCK_CERT_APPS.get(app_id)
    if not app or app["summary"].user_id != user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    return app["detail"]

# ----- CERTIFICATE DOWNLOAD ROUTES -----
@app.get(
    "/epc/certificate/{app_id}/download",
    response_class=FileResponse,
    tags=["Certificate"],
    summary="Download issued certificate PDF"
)
# PUBLIC_INTERFACE
def download_certificate(app_id: str, user: UserInfo = Depends(get_current_user)):
    """
    Lets the user download an issued certificate PDF file, if available.
    """
    app = MOCK_CERT_APPS.get(app_id)
    if not app or app["summary"].user_id != user.id:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["summary"].status != EPCApplicationStatus.ISSUED:
        raise HTTPException(status_code=400, detail="Certificate not yet issued")
    cert_path = MOCK_CERT_FILES.get(app_id)
    if not cert_path or not os.path.exists(cert_path):
        raise HTTPException(status_code=404, detail="Certificate file missing")
    return FileResponse(cert_path, filename=os.path.basename(cert_path))

# ----- ADMIN ROUTES -----
@app.get("/admin/applications", response_model=List[EPCApplicationSummary], tags=["Admin"], summary="List all applications (Admin)")
# PUBLIC_INTERFACE
def admin_list_applications(admin: UserInfo = Depends(get_admin_user)):
    """
    Admin: Lists all certificate applications in the system.
    """
    return [app["summary"] for app in MOCK_CERT_APPS.values()]

@app.get("/admin/application/{app_id}", response_model=EPCApplicationDetail, tags=["Admin"], summary="Get application details (Admin)")
# PUBLIC_INTERFACE
def admin_get_application_detail(app_id: str, admin: UserInfo = Depends(get_admin_user)):
    """
    Admin: View details of a specific certificate application.
    """
    app = MOCK_CERT_APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app["detail"]

@app.post("/admin/application/{app_id}/decision", response_model=EPCApplicationSummary, tags=["Admin"], summary="Update application status (Admin)")
# PUBLIC_INTERFACE
def admin_update_application_status(
    app_id: str,
    action: EPCAdminAction,
    admin: UserInfo = Depends(get_admin_user)
):
    """
    Admin: Update (approve, reject, or set as under review) an application.
    """
    app = MOCK_CERT_APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    summary: EPCApplicationSummary = app["summary"]
    now = datetime.utcnow()
    summary.status = action.status
    summary.last_updated = now
    detail: EPCApplicationDetail = app["detail"]
    detail.status = action.status
    detail.last_updated = now
    detail.admin_notes = action.admin_notes
    return summary

@app.post("/admin/application/{app_id}/upload-certificate", tags=["Admin"], summary="Upload issued certificate PDF (Admin)")
# PUBLIC_INTERFACE
def admin_upload_certificate(
    app_id: str,
    certificate: UploadFile = File(...),
    admin: UserInfo = Depends(get_admin_user)
):
    """
    Admin: Uploads a signed electronic certificate PDF for a given application once it is issued.
    """
    app = MOCK_CERT_APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app["summary"].status != EPCApplicationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Application not approved")
    # "Issue" the certificate: set status and save file
    outdir = "epc_backend/assets/certificates"
    os.makedirs(outdir, exist_ok=True)
    cert_path = os.path.join(outdir, f"cert_{app_id}.pdf")
    with open(cert_path, "wb") as f:
        f.write(certificate.file.read())
    app["summary"].status = EPCApplicationStatus.ISSUED
    app["detail"].status = EPCApplicationStatus.ISSUED
    MOCK_CERT_FILES[app_id] = cert_path
    return {"message": "Certificate uploaded and application marked as ISSUED."}

# ----- HEALTH CHECK -----
@app.get("/", tags=["Health"])
# PUBLIC_INTERFACE
def health_check():
    """Returns a simple health status message."""
    return {"message": "EPC Backend is healthy.", "timestamp": datetime.utcnow().isoformat()}

