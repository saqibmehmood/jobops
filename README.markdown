# JobOps - Internal Ops Management System

A lightweight Django-based system for managing internal operations, including jobs, tasks, equipment, and role-based access for Admins, Technicians, and SalesAgents.

## Project Overview

**JobOps** is a RESTful API built with Django and Django REST Framework (DRF) to manage internal operations. It supports:

- Role-based authentication (Admin, Technician, SalesAgent) using JWT (SimpleJWT).
- Job management with multi-step tasks and equipment assignments.
- Admin panel for managing users, jobs, tasks, and equipment.
- Technician dashboard for viewing assigned jobs and tasks.
- Full CRUD APIs for jobs, tasks, and equipment with role-based permissions.
- Background task to flag overdue jobs using Celery and Redis.
- Management command to generate dummy data for testing.
- Dockerized setup for consistent development and testing.

### Features Implemented

- **Models**:
  - `User`: Custom model with roles (ADMIN, TECHNICIAN, SALES_AGENT).
  - `Job`: Operations with title, client, status, priority, scheduled date, overdue flag.
  - `JobTask`: Ordered tasks within a job, linked to equipment.
  - `Equipment`: Global catalog with name, type, serial number, active status.
- **Admin Panel**: Customized interface for managing all models with filters and search.
- **APIs**:
  - `/api/signup/`: Register users (Admin-only).
  - `/api/login/`: Authenticate and return JWT tokens.
  - `/api/jobs/`: List/create jobs (Admins/SalesAgents create, Technicians see assigned).
  - `/api/jobs/<pk>/`: Retrieve/update/delete jobs (Admins).
  - `/api/tasks/`: List/create tasks (Admins create, Technicians see assigned).
  - `/api/tasks/<pk>/`: Retrieve/update/delete tasks (Admins/Technicians).
  - `/api/equipment/`: List/create equipment (Admins create).
  - `/api/equipment/<pk>/`: Retrieve/update/delete equipment (Admins).
  - `/api/technician/dashboard/`: Technician dashboard for assigned jobs/tasks.
  - `/api/test-auth/`: Test authenticated access.
- **Background Tasks**:
  - Celery task to flag overdue jobs (`scheduled_date < now`, `status != COMPLETED`).
  - Runs daily via Celery Beat.
- **Management Commands**:
  - `generate_dummy_data`: Creates 1 Admin, 2 Technicians, 2 SalesAgents, 5 equipment items, 10 jobs, and 2-5 tasks per job for testing.
- **Docker Setup**:
  - Containers: Django app, PostgreSQL, Redis, Celery worker, Celery Beat.
  - Runs `generate_dummy_data` on app container startup.

## Prerequisites

- Python 3.8+
- Django 4.2+
- PostgreSQL 13
- Redis 6
- Docker and Docker Compose
- For detailed dependencies, see `requirements.txt`.

## Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/saqibmehmood/jobops.git
   cd jobops
   ```

2. **Set Up Environment Variables**: Create a `.env` file in the project root:

   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1 #or domian/ip etc
   DATABASE_NAME=jobops
   DATABASE_USER=postgres
   DATABASE_PASSWORD=postgres
   DATABASE_HOST=db
   DATABASE_PORT=5432
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```

   Generate a secret key:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Build and Run Docker Containers**:

   ```bash
   docker-compose up --build
   ```

   - Starts Django, PostgreSQL, Redis, Celery, and Celery Beat.
   - Runs `generate_dummy_data` on startup, creating test data (1 Admin, 2 Technicians, 2 SalesAgents, 5 equipment items, 10 jobs, 2-5 tasks per job).
   - Access:
     - Admin panel: `http://localhost:8000/admin` (or `http://BaseURL/admin` for local dev or prod)
     - APIs: `http://BaseURL/admin` (or `http://localhost:8000/api/`)

4. **Access Admin Panel**:

   - Open `http://BaseURL/admin` (or `http://localhost:8000/admin`).
   - Log in with:
     - Dummy Admin: Username `admin1`, Password `admin123` (created by `generate_dummy_data`).
     - Or create a superuser:

       ```bash
       docker-compose exec app python manage.py createsuperuser
       ```
     - View/edit `Users`, `Jobs`, `JobTasks`, `Equipment`, and Celery tasks.

5. **Configure Celery Periodic Tasks**:

   - In the admin panel (`http://BaseURL/admin`), go to `Periodic Tasks` (under `django_celery_beat`).
   - Add:
     - Name: “Flag Overdue Jobs”
     - Task: `core.tasks.flag_overdue_jobs`
     - Schedule: Crontab `0 0 * * *` (midnight UTC).
   - Celery worker and Beat run automatically via Docker.

6. **Run Manual Dummy Data (Optional)**:

   ```bash
   docker-compose exec app python manage.py generate_dummy_data --jobs 20
   ```

## Using the Project

1. **Test APIs**:

   - **Login as Technician** (`tech1`):

     ```bash
     curl -X POST http://localhost:8000/api/login/ -H "Content-Type: application/json" -d '{"username":"tech1","password":"tech1123"}'
     ```

     Copy the `access` token from the response.
   - **Check Technician Dashboard**:

     ```bash
     curl -X GET http://localhost:8000/api/technician/dashboard/ -H "Authorization: Bearer <tech1-token>" -H "Content-Type: application/json"
     ```
   - **List Equipment** (Admin-only):

     ```bash
     curl -X GET http://localhost:8000/api/equipment/ -H "Authorization: Bearer <admin-token>" -H "Content-Type: application/json"
     ```
   - **Test Overdue Flagging**:

     ```bash
     docker-compose exec celery celery -A jobops call core.tasks.flag_overdue_jobs
     ```

2. **Verify Data in Admin Panel**:

   - Check `Users`: 5 users (`admin1`, `tech1`, `tech2`, `sales1`, `sales2`).
   - Check `Equipment`: 5 items (Drill, Hammer, etc.).
   - Check `Jobs`: 10 jobs, some with `overdue=True`.
   - Check `JobTasks`: 2-5 tasks per job with equipment.

3. **API Endpoints**:

   - **POST /api/signup/**: Register user (Admin-only).

     ```bash
     curl -X POST http://localhost:8000/api/signup/ -H "Content-Type: application/json" -H "Authorization: Bearer <admin-token>" -d '{"username":"tech2","email":"tech2@example.com","password":"tech12345","role":"TECHNICIAN"}'
     ```
   - **POST /api/login/**: Get JWT tokens.
   - **POST /api/token/refresh/**: Refresh access token.

     ```bash
     curl -X POST http://localhost:8000/api/token/refresh/ -H "Content-Type: application/json" -d '{"refresh":"your-refresh-token"}'
     ```
   - **GET/POST /api/jobs/**: List/create jobs.

     ```bash
     curl -X POST http://localhost:8000/api/jobs/ -H "Content-Type: application/json" -H "Authorization: Bearer <sales-agent-token>" -d '{"title":"Install AC","description":"Install air conditioner","client_name":"ABC Corp","assigned_to_id":2,"status":"PENDING","priority":"MEDIUM","scheduled_date":"2025-08-10T10:00:00Z"}'
     ```
   - **GET/PUT/DELETE /api/jobs//**: Retrieve/update/delete job (Admins).
   - **GET/POST /api/tasks/**: List/create tasks.
   - **GET/PUT/PATCH/DELETE /api/tasks//**: Retrieve/update/delete task.
   - **GET/POST /api/equipment/**: List/create equipment (Admins).
   - **GET/PUT/DELETE /api/equipment//**: Retrieve/update/delete equipment.
   - **GET /api/technician/dashboard/**: Technician dashboard.
   - **GET /api/test-auth/**: Test authenticated access.

     ```bash
     curl -H "Authorization: Bearer <access-token>" http://localhost:8000/api/test-auth/
     ```

## Notes for AWS Deployment

- Push Docker images to GitHub Container Registry (GHCR).
- Deploy on EC2, running Docker containers for Django app, PostgreSQL, and Redis.
- Update `ALLOWED_HOSTS` in `.env` with EC2 public IP or domain.
- Store `SECRET_KEY` in AWS Secrets Manager; fetch via `boto3` in `settings.py`.
- Use a reverse proxy (e.g., Nginx) to serve `http://<your-domain>`.

## Next Steps

- Add job analytics or audit log.
- Optimize EC2 deployment with auto-scaling.