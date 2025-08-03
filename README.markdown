# JobOps

JobOps is a Django REST Framework application for managing job tasks, tailored for technicians, admins, and sales agents. It offers user authentication and a technician dashboard to view upcoming and in-progress tasks grouped by day. Built with PostgreSQL, Redis, Celery, and Docker, it uses GitHub Actions for CI/CD.

## Project Setup

### Prerequisites

- Python 3.8
- Docker and Docker Compose
- GitHub Container Registry (GHCR) access with Personal Access Token (`GHCR_TOKEN`)

### Local Setup

1. **Clone Repository**:

   ```bash
   git clone https://github.com/<yourusername>/jobops.git
   cd jobops
   ```

2. **Set Environment Variables**: Create a `.env` file:

   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,jobops.local
   DATABASE_NAME=jobops
   DATABASE_USER=jobops_user
   DATABASE_PASSWORD=jobops_pass
   DATABASE_HOST=db
   DATABASE_PORT=5432
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```

3. **Run Docker Compose**:

   ```bash
   docker-compose up -d
   ```

   - Migrations and dummy data generation run automatically on startup.

4. **Access Application**:

   - Admin: `baseUrl/admin/` (e.g., `http://localhost:8000/admin/`)
   - API: `baseUrl/api/` (e.g., `http://localhost:8000/api/`)

5. **Stop Containers**:

   ```bash
   docker-compose down
   ```

## Dummy Data Generation

The `generate_dummy_data.py` script automatically populates the database with test users, jobs, tasks, and equipment on Docker startup. It creates:

- **Admin**: `admin1` (password: `admin123`, role: `ADMIN`).
- **Technicians**: `tech1` (password: `tech1123`, role: `TECHNICIAN`), `tech2` (password: `tech2123`, role: `TECHNICIAN`).
- **Sales Agents**: `sales1` (password: `sales1123`, role: `SALES_AGENT`), `sales2` (password: `sales2123`, role: `SALES_AGENT`).
- **Equipment**: Drill, Hammer, Wrench, Crane, Truck.
- **Jobs**: 10 jobs with random statuses (`PENDING`, `IN_PROGRESS`, `COMPLETED`), priorities, and scheduled dates.
- **Tasks**: 2–5 tasks per job with random statuses and equipment.

## System Login

Use these credentials to log in via `/api/login/` or the Django admin (`baseUrl/admin/`):

- **Admin**:
  - Username: `admin1`
  - Password: `admin123`
- **Technicians**:
  - Username: `tech1`, Password: `tech1123`
  - Username: `tech2`, Password: `tech2123`
- **Sales Agents**:
  - Username: `sales1`, Password: `sales1123`
  - Username: `sales2`, Password: `sales2123`

**Example Login**:

```bash
curl -X POST baseUrl/api/login/ -d "username=tech1&password=tech1123"
```

## API Endpoints

All endpoints are accessed at `baseUrl/api/` (e.g., `http://localhost:8000/api/`). Use JSON for requests and responses. Authentication uses JWT tokens obtained via `/api/login/`.

### 1. Signup

- **Endpoint**: `POST /api/signup/`
- **Description**: Create a new user (admin-only).
- **Permissions**: Requires `IsAdmin` permission (admin JWT token).
- **Method**: POST
- **Headers**:

  ```
  Content-Type: application/json
  Authorization: Bearer <admin-jwt-token>
  ```
- **Request Body**:

  ```json
  {
      "username": "newtech",
      "email": "newtech@example.com",
      "password": "newtech123",
      "role": "TECHNICIAN"
  }
  ```
- **Response** (201 Created):

  ```json
  {
      "username": "newtech",
      "email": "newtech@example.com",
      "role": "TECHNICIAN"
  }
  ```
- **Error** (400 Bad Request):

  ```json
  {
      "username": ["A user with that username already exists."]
  }
  ```
- **Error** (403 Forbidden):

  ```json
  {
      "detail": "You do not have permission to perform this action."
  }
  ```

**Example**:

```bash
curl -H "Authorization: Bearer <admin-jwt-token>" -X POST baseUrl/api/signup/ -d '{"username": "newtech", "email": "newtech@example.com", "password": "newtech123", "role": "TECHNICIAN"}'
```

### 2. Login

- **Endpoint**: `POST /api/login/`
- **Description**: Authenticate a user and obtain a JWT token with role.
- **Permissions**: Open to all (no authentication required).
- **Method**: POST
- **Headers**:

  ```
  Content-Type: application/json
  ```
- **Request Body**:

  ```json
  {
      "username": "tech1",
      "password": "tech1123"
  }
  ```
- **Response** (200 OK):

  ```json
  {
      "refresh": "<refresh-token>",
      "access": "<access-token>",
      "role": "TECHNICIAN"
  }
  ```
- **Error** (401 Unauthorized):

  ```json
  {
      "detail": "No active account found with the given credentials"
  }
  ```

**Example**:

```bash
curl -X POST baseUrl/api/login/ -d "username=tech1&password=tech1123"
```

### 3. Technician Dashboard

- **Endpoint**: `GET /api/technician-dashboard/`
- **Description**: Retrieve upcoming and in-progress job tasks for the authenticated technician, grouped by job's scheduled date. Includes job title, task description (as `details`), and required equipment.
- **Permissions**: Requires `IsAuthenticated` and `IsTechnician` (technician JWT token).
- **Method**: GET
- **Headers**:

  ```
  Authorization: Bearer <technician-jwt-token>
  ```
- **Parameters**: None
- **Request Body**: None
- **Response** (200 OK):

  ```json
  [
      {
          "date": "2025-08-03",
          "tasks": [
              {
                  "id": 1,
                  "job_title": "Repair HVAC",
                  "details": "Fix cooling unit",
                  "equipment": [
                      {
                          "id": 1,
                          "name": "Screwdriver",
                          "type": "Tool",
                          "is_active": true
                      }
                  ],
                  "status": "PENDING"
              }
          ]
      },
      {
          "date": "2025-08-04",
          "tasks": [
              {
                  "id": 2,
                  "job_title": "Install Wiring",
                  "details": "Set up electrical panel",
                  "equipment": [
                      {
                          "id": 2,
                          "name": "Wire Cutter",
                          "type": "Tool",
                          "is_active": true
                      }
                  ],
                  "status": "IN_PROGRESS"
              }
          ]
      }
  ]
  ```
- **Error** (401 Unauthorized):

  ```json
  {
      "detail": "Authentication credentials were not provided."
  }
  ```
- **Error** (403 Forbidden):

  ```json
  {
      "detail": "You do not have permission to perform this action."
  }
  ```

**Example**:

```bash
curl -H "Authorization: Bearer <technician-jwt-token>" baseUrl/api/technician-dashboard/
```

## Authentication

- **JWT Tokens**: Obtain via `/api/login/`. Use the `access` token in the `Authorization: Bearer <access-token>` header.
- **Refresh Tokens**: Use `/api/token/refresh/` to refresh tokens (handled by `rest_framework_simplejwt`).
- **Admin Login**: Use `admin1` credentials for `/api/signup/` or Django admin (`baseUrl/admin/`).

## Testing Locally

1. **Start Docker Compose**:

   ```bash
   export SECRET_KEY=test-secret-key
   docker-compose up -d
   ```

   - Migrations and dummy data (`generate_dummy_data.py`) run automatically.

2. **Test Endpoints**:

   ```bash
   # Login as technician
   curl -X POST http://localhost:8000/api/login/ -d "username=tech1&password=tech1123"
   # Test technician dashboard
   curl -H "Authorization: Bearer <technician-jwt-token>" http://localhost:8000/api/technician-dashboard/
   # Login as admin
   curl -X POST http://localhost:8000/api/login/ -d "username=admin1&password=admin123"
   # Test signup
   curl -H "Authorization: Bearer <admin-jwt-token>" -X POST http://localhost:8000/api/signup/ -d '{"username": "newtech", "email": "newtech@example.com", "password": "newtech123", "role": "TECHNICIAN"}'
   ```

3. **Stop Containers**:

   ```bash
   docker-compose down
   ```

## CI

- **GitHub Actions**: Tests run with PostgreSQL (`jobops`, `jobops_user`, `jobops_pass`) and push images to `ghcr.io/<yourusername>/jobops:<commit-sha>`.
- **Verify Image**:

  ```bash
  echo $GHCR_TOKEN | docker login ghcr.io -u <yourusername> --password-stdin
  docker pull ghcr.io/<yourusername>/jobops:<commit-sha>
  # Update docker-compose.yml with <commit-sha>
  docker-compose up -d
  curl -H "Authorization: Bearer <technician-jwt-token>" http://localhost:8000/api/technician-dashboard/
  docker-compose down
  ```