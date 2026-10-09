# DataGuard Backend

Beginner-level hackathon backend for real-time unauthorized employee data exfiltration detection.

## Architecture

React -> FastAPI -> Detection Engine -> SQLite/PostgreSQL -> WebSocket -> React

No Kafka, MQTT, Redis, RabbitMQ, Celery or external queue is used.

## Features

- Users and roles
- File sensitivity classification
- Per-user file permissions
- Synthetic activity events
- Rule-based detection
- Risk scoring
- Isolation Forest anomaly detection
- Real-time WebSocket alerts
- User activity timeline
- Dashboard statistics
- Analyst-approved exceptions
- Demo event simulator

## Setup - Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000/docs

## Demo scenarios

Open another terminal with the venv activated:

```powershell
python simulator/event_generator.py --scenario unauthorized_download
python simulator/event_generator.py --scenario usb_exfiltration
python simulator/event_generator.py --scenario personal_cloud
python simulator/event_generator.py --scenario personal_email
```

Or all:

```powershell
python simulator/event_generator.py --scenario all
```

## Demo data

Users:
1. Rahul Sharma - HR Executive
2. Priya Verma - Finance Executive
3. Amit Singh - Developer
4. Neha Patel - Manager

Files:
1. company_logo.png - PUBLIC
2. employee_policy.pdf - INTERNAL
3. employee_salary.xlsx - CONFIDENTIAL
4. patient_records.xlsx - HIGHLY_SENSITIVE
5. company_database.sql - CRITICAL
6. quarterly_financial_report.xlsx - CONFIDENTIAL

## WebSocket

React connects to:

ws://127.0.0.1:8000/ws/alerts

A new alert is pushed immediately when detection creates one.

## User creation and file permission assignment

This prototype now supports creating users and managing per-user file permissions from the UI.

- `POST /api/users` — create user (`name`, `email`, `department`, `role`, optional `is_active`)
- `PATCH /api/users/{id}` — update user
- `GET /api/users/{id}/permissions` — list file permissions
- `PUT /api/users/{id}/permissions/{file_id}` — upsert `can_read`, `can_download`, `can_share`, `can_copy`
- `DELETE /api/users/{id}/permissions/{file_id}` — revoke the permission assignment
- `GET /api/files/{id}` — includes assigned users and their permissions

Permission example:

```json
{"can_read": true, "can_download": false, "can_share": false, "can_copy": false}
```

**Security limitation:** this hackathon prototype does not include authentication/roles for API callers. User/permission management endpoints are therefore not protected against arbitrary callers. Do not expose it to the public internet or treat it as production-ready until authentication and administrator authorization are implemented. Permission checks on ingested telemetry detect/log simulated unauthorized operations; they do not by themselves block a real operating-system file transfer.

## Main APIs

POST /api/events
GET /api/events

GET /api/alerts
GET /api/alerts/{id}
PATCH /api/alerts/{id}

GET /api/users
POST /api/users
GET /api/users/{id}
PATCH /api/users/{id}
GET /api/users/{id}/activity
GET /api/users/{id}/risk
GET /api/users/{id}/permissions
PUT /api/users/{id}/permissions/{file_id}
DELETE /api/users/{id}/permissions/{file_id}

GET /api/files
GET /api/files/{id}

GET /api/dashboard/summary
GET /api/dashboard/risk-trend
GET /api/dashboard/recent-alerts

GET /api/exceptions
POST /api/exceptions
DELETE /api/exceptions/{id}

## Detection flow

1. Event arrives.
2. User and file are loaded.
3. Permission is checked.
4. File sensitivity and action rules are evaluated.
5. Behaviour is checked with Isolation Forest when enough history exists.
6. Risk score and severity are calculated.
7. Suspicious events create alerts.
8. Alert is stored in the database.
9. Alert is sent through WebSocket.
10. React displays the alert immediately.

## Production note

This is a hackathon prototype. The simulator represents endpoint/email/cloud/device telemetry. A production implementation would connect approved enterprise data sources and endpoint agents instead of simulating events.
