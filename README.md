# CivicSaathi

**AI-powered Municipal Complaint Management System** — a full-stack application for filing, routing, and resolving civic complaints with automated AI verification, smart duplicate detection, and SLA-driven escalation.

Built with **Django REST Framework** + **Next.js** + **Google Gemini AI**.

---

## Features

### Multi-Role Access
- **Citizens** — File complaints, track status, upvote issues
- **Root Admin (ULB)** — Full system oversight across 14 departments
- **Sub-Admins** — Cluster-level management (4 clusters)
- **Department Admins** — Department + city-scoped operations
- **Workers** — Field resolution with in-app notifications

### AI-Powered Complaint Pipeline
- **Image Analysis** — Gemini Vision auto-generates title, department, description from uploaded photos
- **Two-Stage Filtering** — NLP spam detection (Filter A) + AI image verification (Filter B)
- **Dynamic SLA & Priority** — AI determines SLA hours (2–48h), priority (1–5), and emergency flags
- **Smart Duplicate Detection** — Semantic hashing with synonym matching, geo-proximity (~30m grid), and fuzzy title comparison

### Automated Routing
- **Sorting Layer A** — Auto-routes to correct department
- **Sorting Layer B** — Auto-assigns city office (matches department + citizen's city)
- **Worker Assignment** — Load-balanced selection of least-busy active worker

### Complaint Lifecycle
```
SUBMITTED → FILTERING → [DECLINED / PENDING_VERIFICATION / VERIFIED]
                                        ↓
SORTING → PENDING → ASSIGNED → IN_PROGRESS → RESOLVED → COMPLETED
                                              (or REJECTED at any admin stage)
```

### SLA & Escalation
- Per-category SLA configs (resolution + escalation hours)
- Auto-escalation at 80% of SLA deadline with warning emails
- Priority bumping and reassignment on SLA breach
- Cron-ready management command with `--dry-run` support

### Other
- **Upvote system** — Boosts effective priority; auto-upvotes on duplicate submissions
- **Multi-channel notifications** — In-app bell + email alerts for assignments, SLA warnings, escalations
- **Worker attendance** — Daily tracking with bulk mark, half-day, and leave support
- **Comprehensive audit trail** — Every status change, assignment, and AI decision is logged

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Django REST Framework |
| Frontend | Next.js 14, React 18, Axios |
| AI/ML | Google Gemini 2.5 Flash (Vision API) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | DRF Token auth (citizens/workers) + custom header auth (admins) |
| Email | Django SMTP (Gmail) |
| Admin UI | django-jazzmin |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key (for AI features)

### Backend

```bash
cd CivicSaathi
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend runs at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

### Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-gemini-api-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=CivicSaathi <civicsaathi@gmail.com>
SITE_URL=http://localhost:8000
```

---

## Project Structure

```
CivicSaathi/
├── civic_saathi/              # Main Django app
│   ├── models.py              # 20 models (User, Complaint, Department, Worker, SLA, etc.)
│   ├── views_api.py           # REST API views
│   ├── urls.py                # API routing
│   ├── serializers.py         # DRF serializers
│   ├── ai_filter.py           # Gemini Vision integration
│   ├── duplicate_detection.py # Smart hash duplicate detection
│   ├── filter_system.py       # Two-stage NLP + AI filter pipeline
│   ├── email_service.py       # Multi-channel email notifications
│   ├── admin_auth.py          # Custom admin authentication
│   ├── permissions.py         # Role-based permission classes
│   ├── signals.py             # Django signals
│   └── management/commands/
│       └── auto_escalate.py   # SLA auto-escalation (cron-ready)
├── municipal/                 # Django project config
│   ├── settings.py
│   └── urls.py
├── frontend/                  # Next.js app
│   ├── pages/                 # Citizen, Admin, Worker portals
│   ├── components/            # Navbar, SLATimerCard, NotificationBell
│   ├── context/               # Auth contexts (Citizen, Admin, Worker)
│   └── utils/                 # API clients (api.js, adminApi.js, workerApi.js)
├── adminCredentials.json      # Admin login credentials
├── requirements.txt
└── manage.py
```

---

## API Endpoints

All endpoints are prefixed with `/api/`.

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `auth/register/` | Citizen registration |
| POST | `auth/login/` | Citizen login |
| POST | `auth/logout/` | Logout (deletes token) |
| GET | `auth/me/` | Current user info |
| POST | `worker/login/` | Worker login |
| GET | `worker/me/` | Current worker details |

### Complaints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `complaints/analyze-image/` | AI image analysis (pre-submission) |
| POST | `complaints/create/` | Create complaint (triggers full pipeline) |
| GET | `complaints/all/` | All complaints (filterable) |
| GET | `complaints/my/` | Current user's complaints |
| GET | `complaints/upvoted/` | User's upvoted complaints |
| GET | `complaints/<id>/` | Complaint detail |
| POST | `complaints/<id>/upvote/` | Toggle upvote |
| GET | `complaints/<id>/logs/` | Audit trail |

### Admin Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `department/complaints/` | Dept-scoped complaints |
| POST | `complaints/<id>/verify/` | Manual verification |
| POST | `complaints/<id>/assign/` | Assign to worker |
| POST | `complaints/<id>/update-status/` | Update status |
| POST | `complaints/<id>/reject/` | Reject complaint |
| DELETE | `complaints/<id>/delete/` | Soft-delete |
| POST | `complaints/<id>/reassign/` | Reassign department |
| POST | `complaints/<id>/assign-office/` | Manual office assignment |

### Worker
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `worker/assignments/` | Assigned complaints |
| GET | `worker/dashboard/stats/` | Dashboard stats |
| POST | `worker/complaints/<id>/complete/` | Mark completed (with image proof) |
| GET | `worker/notifications/` | Notifications (supports `?unread_only=true`) |
| POST | `worker/notifications/<id>/read/` | Mark notification read |
| POST | `worker/notifications/mark-all-read/` | Mark all read |

### SLA & Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `sla/configs/` | List SLA configurations |
| PUT | `sla/configs/<id>/` | Update SLA config |
| GET | `sla/report/` | SLA compliance report |
| POST | `sla/trigger-escalation/` | Manual escalation check (supports `dry_run`) |

### Resources
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `departments/` | All departments |
| GET | `categories/` | Complaint categories |
| GET/POST | `offices/`, `offices/create/` | List / create offices |
| GET/POST | `workers/`, `workers/create/` | List / create workers |
| GET | `workers/<id>/statistics/` | Worker performance stats |
| GET | `dashboard/stats/` | Role-based dashboard statistics |
| POST | `attendance/mark/` | Mark attendance |
| POST | `attendance/bulk-mark/` | Bulk attendance |
| GET | `attendance/register/` | Attendance register |

---

## Frontend Pages

### Citizen Portal
| Page | Path |
|------|------|
| Landing | `/` |
| Login / Register | `/login`, `/register` |
| Dashboard | `/dashboard` |
| File Complaint | `/complaints/new` |
| My Complaints | `/complaints` |
| All Complaints | `/complaints/all` |
| Complaint Detail | `/complaints/[id]` |
| Upvoted | `/complaints/upvoted` |
| By Status | `/complaints/status/{pending,in-progress,completed,declined}` |

### Admin Portal
| Page | Path |
|------|------|
| Login / Dashboard | `/admin/login`, `/admin/dashboard` |
| Complaints | `/admin/complaints`, `/admin/complaints/[id]` |
| By Status | `/admin/complaints/status/{pending,in-progress,completed,rejected}` |
| Workers | `/admin/workers`, `/admin/workers/add`, `/admin/workers/[id]` |
| Offices | `/admin/offices`, `/admin/offices/add`, `/admin/offices/[id]` |
| Departments | `/admin/departments` |
| Attendance | `/admin/attendance` |
| SLA Config | `/admin/sla` |
| Settings | `/admin/settings` |

### Worker Portal
| Page | Path |
|------|------|
| Login / Dashboard | `/worker/login`, `/worker/dashboard` |
| Assigned / Pending | `/worker/assigned`, `/worker/pending` |
| Completed / Overdue | `/worker/completed`, `/worker/overdue` |
| Complaint Detail | `/worker/complaint/[id]` |

---

## Database Models

| Model | Purpose |
|-------|---------|
| `CustomUser` | Extended user with roles (Citizen, Admin, Sub-Admin, Dept-Admin, Worker) |
| `Department` | 14 municipal departments |
| `SubAdminCategory` | 4 department clusters |
| `ComplaintCategory` | Problem types mapped to departments |
| `AdminProfile` / `SubAdminProfile` / `DepartmentAdminProfile` | Role-specific admin profiles |
| `Office` | Department offices by city |
| `Worker` | Field staff with department + office assignment |
| `Complaint` | Core model — 12 status states, AI-determined priority/SLA, smart hash |
| `ComplaintLog` | Immutable audit trail |
| `ComplaintVote` | Upvote records |
| `ComplaintEscalation` | SLA breach escalation records |
| `SLAConfig` | Per-category resolution + escalation hours |
| `AIVerificationLog` | Gemini Vision verification audit log |
| `WorkerNotification` | In-app notifications with read tracking |
| `WorkerAttendance` / `DepartmentAttendance` | Attendance system |

---

## Management Commands

```bash
# Auto-escalate overdue complaints (cron-ready)
python manage.py auto_escalate

# Dry run (no changes, just report)
python manage.py auto_escalate --dry-run

# Custom warning threshold (default: 80%)
python manage.py auto_escalate --warning-threshold 0.7
```

---

## Deployment

- Set `DEBUG=False` and configure `SECRET_KEY`
- Switch to PostgreSQL (`psycopg` included in requirements)
- Configure `ALLOWED_HOSTS` and CORS origins
- Run `python manage.py collectstatic`
- Deploy with gunicorn behind Nginx
- Set up cron for `auto_escalate` command
- Configure Gmail SMTP or production email backend

---

## License

Developed for the VGU Hackathon. All rights reserved.
