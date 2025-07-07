# EPC Backend REST API Endpoint Reference

This document provides a comprehensive overview of the REST API endpoints implemented in the FastAPI backend for the Vanuatu Police Electronic Police Certificate (EPC) system. It is intended to guide frontend integration and to clarify capabilities currently supported by the backend.

---

## Table of Contents

- [Authentication Endpoints](#authentication-endpoints)
- [User Endpoints](#user-endpoints)
- [Certificate Application Endpoints](#certificate-application-endpoints)
- [Certificate Management Endpoints](#certificate-management-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Health Check](#health-check)
- [Summary Table](#summary-table)
- [Appendix: Models and Enums](#appendix-models-and-enums)

---

## Authentication Endpoints

### Register New User

- **URL:** `/auth/register`
- **Method:** POST
- **Summary:** Register a new user.
- **Request Body:**
    - `email` (string, required): User's email address.
    - `password` (string, required): Password (min 6 chars).
    - `full_name` (string, required): User's full name.
    - `phone` (string, optional): Contact phone.
- **Response:** JWT access token and token type.

### Login

- **URL:** `/auth/login`
- **Method:** POST
- **Summary:** User login, returns access token.
- **Request Body:**
    - `username` (string, required): User's email (OAuth2 form).
    - `password` (string, required)
- **Response:** JWT access token and token type.

---

## User Endpoints

### Get Current User

- **URL:** `/auth/me`
- **Method:** GET
- **Summary:** Get details of the currently authenticated user.
- **Headers:** `Authorization: Bearer {access_token}`
- **Response:** User details (id, email, full_name, is_admin, status).

---

## Certificate Application Endpoints

### Submit Certificate Application

- **URL:** `/epc/application`
- **Method:** POST
- **Summary:** Submit a new police certificate application.
- **Headers:** `Authorization: Bearer {access_token}`
- **Request Body:**
    - `purpose` (string, required)
    - `passport_number` (string, required)
    - `country_of_application` (string, required)
    - `address` (string, required)
- **Response:** Application summary.

### List User's Applications

- **URL:** `/epc/application`
- **Method:** GET
- **Summary:** Get a list of police certificate applications submitted by the authenticated user.
- **Headers:** `Authorization: Bearer {access_token}`
- **Response:** Array of application summaries.

### Get Application Details

- **URL:** `/epc/application/{app_id}`
- **Method:** GET
- **Summary:** Get details for a single police certificate application.
- **Headers:** `Authorization: Bearer {access_token}`
- **URL Params:**
    - `app_id` (string, required)
- **Response:** Complete application detail, including purpose, passport number, country, address, status, and admin notes.

---

## Certificate Management Endpoints

### Download Issued Certificate

- **URL:** `/epc/certificate/{app_id}/download`
- **Method:** GET
- **Summary:** Download the PDF of an issued police certificate (if available).
- **Headers:** `Authorization: Bearer {access_token}`
- **URL Params:**
    - `app_id` (string, required)
- **Response:** Returns a PDF as a file download if the certificate has been issued.

---

## Admin Endpoints

All admin endpoints require an authenticated user with `is_admin: true`.

### List All Applications (Admin)

- **URL:** `/admin/applications`
- **Method:** GET
- **Summary:** Admin: List all police certificate applications in the system.
- **Headers:** `Authorization: Bearer {access_token}`

### Get Application Details (Admin)

- **URL:** `/admin/application/{app_id}`
- **Method:** GET
- **Summary:** Admin: Get details for a specific application.
- **Headers:** `Authorization: Bearer {access_token}`
- **URL Params:**
    - `app_id` (string, required)

### Admin: Update Application Status

- **URL:** `/admin/application/{app_id}/decision`
- **Method:** POST
- **Summary:** Admin: Update status (approve, reject, under review) for an application.
- **Headers:** `Authorization: Bearer {access_token}`
- **Request Body:**
    - `status` (string, required): One of `SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `ISSUED`
    - `admin_notes` (string, optional)

### Admin: Upload Issued Certificate

- **URL:** `/admin/application/{app_id}/upload-certificate`
- **Method:** POST (multipart/form-data)
- **Summary:** Admin: Upload a signed PDF certificate and mark the application as issued.
- **Headers:** `Authorization: Bearer {access_token}`
- **Form Data:**
    - `certificate` (file, required): PDF file to be uploaded.

---

## Health Check

### System Health

- **URL:** `/`
- **Method:** GET
- **Summary:** Returns a simple status message verifying backend health.
- **Response:** Message and timestamp.

---

## Summary Table

| Path                                       | Method | Tag         | Auth Required | Summary                                      |
|---------------------------------------------|--------|-------------|--------------|----------------------------------------------|
| `/auth/register`                           | POST   | Auth        | No           | Register new user                            |
| `/auth/login`                              | POST   | Auth        | No           | Login (get token)                            |
| `/auth/me`                                 | GET    | Auth        | Yes          | Get current user info                        |
| `/epc/application`                         | POST   | Application | Yes          | Submit police certificate application         |
| `/epc/application`                         | GET    | Application | Yes          | Get user's applications                      |
| `/epc/application/{app_id}`                | GET    | Application | Yes          | Get application details                      |
| `/epc/certificate/{app_id}/download`       | GET    | Certificate | Yes          | Download issued certificate                   |
| `/admin/applications`                      | GET    | Admin       | Yes (Admin)  | List all applications                        |
| `/admin/application/{app_id}`              | GET    | Admin       | Yes (Admin)  | Get application detail                       |
| `/admin/application/{app_id}/decision`     | POST   | Admin       | Yes (Admin)  | Update application status                    |
| `/admin/application/{app_id}/upload-certificate` | POST   | Admin | Yes (Admin)  | Upload/issue certificate PDF                  |
| `/`                                        | GET    | Health      | No           | Health check                                 |

---

## Appendix: Models and Enums

- **Auth Models**: `UserRegistration`, `UserInfo`, `TokenResponse`
- **Application Models**: `EPCApplicationRequest`, `EPCApplicationSummary`, `EPCApplicationDetail`
- **Admin Models**: `EPCAdminAction`
- **Enums**: `EPCApplicationStatus` (SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, ISSUED)

---

This documentation is automatically extracted from the backend FastAPI implementation, and accurately reflects the available endpoints, required parameters, and authentication requirements. 
