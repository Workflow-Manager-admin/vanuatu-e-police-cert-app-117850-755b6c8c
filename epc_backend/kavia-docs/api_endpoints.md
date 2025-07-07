# EPC Backend: REST API Endpoints Documentation

This document describes all REST API endpoints implemented by the Electronic Police Certificate (EPC) backend (FastAPI), including their purposes, request/response models, and intended user or admin roles.

---

## Table of Contents

- [Authentication and User Management](#authentication-and-user-management)
- [Certificate Application](#certificate-application)
- [Certificate Download](#certificate-download)
- [Administrative Operations](#administrative-operations)
- [Health Check](#health-check)
- [Summary Table](#summary-table)

---

## Authentication and User Management

### Register a New User
- **POST /auth/register**
- **Purpose:** Registers a new applicant user with email, password, name, and phone (optional).
- **Request Body:**  
  ```json
  {
    "email": "applicant@email.com",
    "password": "string (min 6 chars)",
    "full_name": "string",
    "phone": "string (optional)"
  }
  ```
- **Response:**  
  ```json
  { "access_token": "string", "token_type": "bearer" }
  ```
- **Notes:** Returns a bearer token on successful registration. Email must be unique.

---

### User Login (Token Acquisition)
- **POST /auth/login**
- **Purpose:** Authenticates user; returns access token for session.
- **Request Body:** Form fields (`application/x-www-form-urlencoded`):
  - username: User email
  - password: User password
- **Response:**  
  ```json
  { "access_token": "string", "token_type": "bearer" }
  ```
- **Notes:** Token is required for all further user actions.

---

### Get Current User Info
- **GET /auth/me**
- **Purpose:** Retrieves details on the currently authenticated user.
- **Auth:** Bearer token required.
- **Response:**  
  ```json
  {
    "id": "string",
    "email": "string",
    "full_name": "string",
    "is_admin": "bool",
    "status": "string"
  }
  ```

---

## Certificate Application

### Submit a Certificate Application
- **POST /epc/application**
- **Purpose:** Submit a new police certificate application.
- **Auth:** Bearer token required (applicant).
- **Request Body:**  
  ```json
  {
    "purpose": "string",
    "passport_number": "string",
    "country_of_application": "string",
    "address": "string"
  }
  ```
- **Response:**  
  Summary of the application created.
  ```json
  {
    "id": "string",
    "user_id": "string",
    "date_submitted": "datetime (ISO)",
    "purpose": "string",
    "status": "SUBMITTED",
    "last_updated": "datetime (ISO)"
  }
  ```

---

### List User Certificate Applications
- **GET /epc/application**
- **Purpose:** List all certificate applications submitted by the authenticated user.
- **Auth:** Bearer token required (applicant).
- **Response:**  
  Array of summaries as shown above.

---

### Get Application Details
- **GET /epc/application/{app_id}**
- **Purpose:** Retrieve full detail of a specific application submitted by the user.
- **Auth:** Bearer token required (applicant).
- **Response:**  
  Detailed application info including status, passport, country, address, admin notes.

---

## Certificate Download

### Download Issued Certificate PDF
- **GET /epc/certificate/{app_id}/download**
- **Purpose:** Download the final, signed police certificate (PDF), if issued.
- **Auth:** Bearer token required (applicant).
- **Response:** Binary PDF file (application/pdf).
- **Notes:** Returns 404 or 400 if not issued or not found.

---

## Administrative Operations

### List All Applications (Admin)
- **GET /admin/applications**
- **Purpose:** Lists all applications in the system (admin only).
- **Auth:** Bearer token (admin).
- **Response:** Array of all application summaries.

---

### Get Application Detail (Admin)
- **GET /admin/application/{app_id}**
- **Purpose:** Show details of a given applicant's certificate request.
- **Auth:** Bearer token (admin).
- **Response:** Full application detail.

---

### Approve, Reject, or Update Application Status (Admin)
- **POST /admin/application/{app_id}/decision**
- **Purpose:** Approve, reject, or update an application's status. May set admin notes.
- **Auth:** Bearer token (admin).
- **Request Body:**  
  ```json
  {
    "status": "UNDER_REVIEW|APPROVED|REJECTED|ISSUED",
    "admin_notes": "string (optional)"
  }
  ```
- **Response:** Updated summary of the application.

---

### Upload Issued Certificate (PDF) (Admin)
- **POST /admin/application/{app_id}/upload-certificate**
- **Purpose:** Allows admin to upload a signed certificate PDF for a given application (when approved).
- **Auth:** Bearer token (admin).
- **Request:** Multipart/form-data field `certificate` (PDF file).
- **Response:**  
  ```json
  { "message": "Certificate uploaded and application marked as ISSUED." }
  ```
- **Notes:** Can only upload when application is approved.

---

## Health Check

### API Health Status
- **GET /**
- **Purpose:** Quickly check if the backend API is responsive.
- **Response:**  
  ```json
  { "message": "EPC Backend is healthy.", "timestamp": "string (ISO)" }
  ```

---

## Summary Table

| Endpoint                                               | Method | Purpose                                   | Role        | Integration Required              |
|--------------------------------------------------------|--------|-------------------------------------------|-------------|-----------------------------------|
| /auth/register                                         | POST   | User registration                        | Any/applicant | Yes                               |
| /auth/login                                            | POST   | User authentication (token)              | Any          | Yes                               |
| /auth/me                                               | GET    | Current user info                        | Any (token)  | Yes                               |
| /epc/application                                       | POST   | Submit new certificate application       | Applicant    | Yes                               |
| /epc/application                                       | GET    | List user's applications                 | Applicant    | Yes                               |
| /epc/application/{app_id}                              | GET    | Application details (user)               | Applicant    | Yes                               |
| /epc/certificate/{app_id}/download                     | GET    | Download issued certificate (PDF)        | Applicant    | Yes                               |
| /admin/applications                                    | GET    | List all applications                    | Admin        | Yes (Admin UI)                    |
| /admin/application/{app_id}                            | GET    | View application in detail               | Admin        | Yes (Admin UI)                    |
| /admin/application/{app_id}/decision                   | POST   | Approve/reject/set status                | Admin        | Yes (Admin UI)                    |
| /admin/application/{app_id}/upload-certificate         | POST   | Upload signed certificate PDF            | Admin        | Yes (Admin UI)                    |
| /                                                     | GET    | Health check                             | Any          | (For monitoring only)             |

---

### Notes

- All authenticated endpoints require a `Bearer` token in the `Authorization` header.
- Admin endpoints require the authenticated user to be an admin.
- Application status values: `SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `ISSUED`.
- Most endpoints return `HTTPException` error codes for unauthorized, forbidden, not found, or invalid requests as per FastAPI conventions.

---
