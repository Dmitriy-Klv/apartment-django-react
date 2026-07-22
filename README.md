<div align="center">

# SoftStay

**A full-stack apartment rental platform** — Django REST Framework + React

*Listings, search & filtering, booking lifecycle, reviews, and history — built as a portfolio project.*

<img src="frontend/src/assets/images/hero-villa.jpg" alt="SoftStay" width="720" />

[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen)](LICENCE)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-5-092e20)
![React](https://img.shields.io/badge/react-19-61dafb)
![Tests](https://img.shields.io/badge/tests-220%20passing-success)
![Coverage](https://img.shields.io/badge/coverage-100%25-success)
![Stack](https://img.shields.io/badge/dependencies-100%25%20free%20%26%20open%20source-informational)

</div>

> This is a demo/portfolio project, not a live commercial service. No real bookings or payments take place.

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Testing](#testing)
- [License](#license)

## Features

| | |
|---|---|
| **Authentication** | JWT-based registration and login with two roles: Tenant and Lessor |
| **Listings** | Full CRUD, up to 5 photos per listing with cover photo selection, soft delete, active/inactive toggle |
| **Search & filtering** | Keyword search, filter by city, district, price range, room count, property type; sorting by price, date, popularity; pagination |
| **Booking** | Full lifecycle (pending → confirmed/rejected → checked-in), overlap detection, cancellation window, role-based permissions |
| **Reviews & ratings** | One review per completed stay, cached average rating and count on the listing |
| **Search & view history** | Per-user history, aggregated "popular searches" and "trending listings" endpoints |
| **Account deletion** | Self-service, password-confirmed, anonymizes the account instead of cascading deletes |
| **API documentation** | Swagger UI and ReDoc via drf-spectacular |

## Tech stack

<table>
<tr><td valign="top">

**Backend**

![Python](https://img.shields.io/badge/-Python%203.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django%205-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/-Django%20REST%20Framework-A30000?logo=django&logoColor=white)
![JWT](https://img.shields.io/badge/-SimpleJWT-000000?logo=jsonwebtokens&logoColor=white)
![MySQL](https://img.shields.io/badge/-MySQL%208-4479A1?logo=mysql&logoColor=white)
![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white)
![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?logo=gunicorn&logoColor=white)
![Pytest](https://img.shields.io/badge/-Pytest-0A9EDC?logo=pytest&logoColor=white)

django-environ · django-filter · django-cors-headers · Pillow · PyMySQL · drf-spectacular · factory-boy · pytest-cov

</td><td valign="top">

**Frontend**

![React](https://img.shields.io/badge/-React%2019-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/-Vite-646CFF?logo=vite&logoColor=white)
![Tailwind](https://img.shields.io/badge/-Tailwind%20CSS%204-06B6D4?logo=tailwindcss&logoColor=white)
![React Router](https://img.shields.io/badge/-React%20Router-CA4245?logo=reactrouter&logoColor=white)
![TanStack Query](https://img.shields.io/badge/-TanStack%20Query-FF4154?logo=reactquery&logoColor=white)
![Axios](https://img.shields.io/badge/-Axios-5A29E4?logo=axios&logoColor=white)

shadcn/ui (Radix UI) · React Hook Form · Zod · Framer Motion · Leaflet

</td></tr>
<tr><td colspan="2" valign="top">

**Infrastructure**

![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/-Nginx-009639?logo=nginx&logoColor=white)

Nginx reverse-proxies the API and Django admin, serves the React build and static/media files, and gates the demo deployment behind HTTP Basic Auth.

</td></tr>
</table>

## Project structure

```
apps/            Django apps: users, listings, bookings, reviews, history
config/          Django settings, URLs, WSGI/ASGI entry points
frontend/        React application (Vite)
docker/          Dockerfiles and Nginx configuration
docker-compose.yml
requirements.txt
```

Each Django app follows the same internal layout: `models/`, `serializers/`, `views/`, `urls/`, `services/` (business logic separated from views), plus `filters/`, `permissions/`, or `signals/` where relevant.

## Getting started

### Backend

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create `.env.dev` in the project root with at least:

```
SECRET_KEY=dev-only-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
MYSQL=False
```

Then:

```bash
python manage.py migrate
python manage.py runserver
```

With `MYSQL=False` the backend uses SQLite — no database server needed to get started. Set `MYSQL=True` and add `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` to run against MySQL instead.

API docs (staff only — see below): `http://localhost:8000/api/schema/swagger-ui/`

To view the API docs, create a staff account and log in via the Django admin session first:

```bash
python manage.py createsuperuser
```

Then open `http://localhost:8000/admin/login/`, log in, and open `http://localhost:8000/api/schema/swagger-ui/` in the same browser tab.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` and expects the backend at `http://localhost:8000` (configurable via `frontend/.env.development`).

### Running with Docker

```bash
cp .env.example .env   # fill in production values, including BASIC_AUTH_USER/PASSWORD
docker compose build
docker compose up -d
```

This starts MySQL, the Django backend (gunicorn), and Nginx serving the React build and proxying `/api/` and `/admin/` to the backend. See `docker-compose.yml` and `docker/nginx.conf` for details.

## Testing

```bash
pytest
pytest --cov=apps --cov-report=term-missing   # with coverage
```

**220 tests, 100% line coverage** on `apps/` (migrations and boilerplate excluded via `.coveragerc`).

## License

[MIT](LICENCE)
