# Electronic Police Certificate Backend API: Endpoint Documentation

This document provides a thorough reference to all REST API endpoints implemented in the FastAPI backend for the Vanuatu Electronic Police Certificate project. Each endpoint summary describes its HTTP method, URL, expected request data, authentication requirements, and response schema. This documentation is useful for frontend developers or system integrators aligning user flows to the backend.

---

## Table of Contents

- [Authentication & User Management](#authentication--user-management)
- [Applicant Certificate Application](#applicant-certificate-application)
- [Application Status Tracking](#application-status-tracking)
- [Certificate Download](#certificate-download)
- [Administrative Endpoints](#administrative-endpoints)
- [System Health Check](#system-health-check)

---

## Authentication & User Management

### Register new user

- **POST** `/auth/register`
- **Request:** JSON body (UserRegistration): `{email, password, full_name, phone?}`
- **Response:** `{access_token, token_type}`
- **Authentication:** None required.
- **Purpose:** Registers a new applicant in the system and returns a bearer token upon success.

### Login (issue token)

- **POST** `/auth/login` (form fields: username, password)
- **Response:** `{access_token, token_type}`
- **Authentication:** None required.
- **Purpose:** Authenticate with credentials and obtain authorization token.

### Get current user info

- **GET** `/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** User profile (id, email, full_name, is_admin, status)
- **Authentication:** Required (valid user token).

---

## Applicant Certificate Application

### Submit new certificate application

- **POST** `/epc/application`
- **Headers:** `Authorization: Bearer <token>`
- **Request:** JSON body (`EPCApplicationRequest`): `{purpose, passport_number, country_of_application, address}`
- **Response:** Application summary (`EPCApplicationSummary`)
- **Authentication:** Required (user).

### List current user's applications

- **GET** `/epc/application`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** List of application summaries for the user.
- **Authentication:** Required (user).

### Get application detail

- **GET** `/epc/application/{app_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Application detail for specified application.
- **Authentication:** Required (user, must own application).

---

## Application Status Tracking

See the endpoints above under [Applicant Certificate Application]. Each submitted application has a status field exposed in the summary/detail return payloads.

---

## Certificate Download

### Download issued certificate PDF

- **GET** `/epc/certificate/{app_id}/download`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** PDF file download (for issued certificate).
- **Authentication:** Required (must be applicant of record, certificate must be issued).

---

## Administrative Endpoints

> All endpoints in this section require the requester to have admin rights (valid admin token).

### List all applications (Admin Dashboard)

- **GET** `/admin/applications`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** List of all application summaries (all users).

### Get application detail (Admin)

- **GET** `/admin/application/{app_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Application detail for any user.

### Application decision (Approve/Reject/Review)

- **POST** `/admin/application/{app_id}/decision`
- **Headers:** `Authorization: Bearer <token>`
- **Request:** JSON body (`EPCAdminAction`): `{status, admin_notes?}`
- **Response:** Updated application summary.

### Upload issued certificate PDF

- **POST** `/admin/application/{app_id}/upload-certificate`
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `multipart/form-data` (field: `certificate` PDF file)
- **Response:** `{message: ...}`

---

## System Health Check

- **GET** `/`
- **Purpose:** Quick health/status check endpoint (no authentication required).

---

## Endpoint Overview Diagram

```mermaid
flowchart TD
    subgraph Auth
      A1([POST /auth/register]) -->|Creates| U[(User)]
      A2([POST /auth/login]) -->|Issues| T[(Token)]
      A3([GET /auth/me]) -->|Returns| U
    end
    subgraph Application
      B1([POST /epc/application]) -->|Creates| AP[(Application)]
      B2([GET /epc/application]) -.-> AP
      B3([GET /epc/application/{app_id}]) -.-> AP
    end
    subgraph Certificate
      C1([GET /epc/certificate/{app_id}/download]) -.-> AP
    end
    subgraph Admin
      D1([GET /admin/applications]) --> AP
      D2([GET /admin/application/{app_id}]) --> AP
      D3([POST /admin/application/{app_id}/decision]) --> AP
      D4([POST /admin/application/{app_id}/upload-certificate]) --> AP
    end
    subgraph Health
      H1([GET /]) 
    end
    A1 -.->|Receives token| A2
    U --> B1
    U --> B2
    U --> B3
    U --> C1
    U --> D1
    U --> D2
    U --> D3
    U --> D4
    H1 -. Healthcheck .- H1
```

---

**Endpoint Security Summary:**  
- Most endpoints require a bearer token. Admin routes require an admin role.
- Endpoints for registration and login are public.
- Health check is public.
- File download and upload operations use binary/multipart responses.

---

**Note:**  
- The backend implementation uses in-memory mock data and simple validation for development.  
- All interactions are to be switched to real persistent data and secure password hashing before production.  
- Adjust clients to use the correct Authorization header: `Authorization: Bearer <token>`.

---

_This document was generated by analyzing the `src/api/main.py` FastAPI application._
