# JobOps - Internal Ops Management System

A lightweight Django-based system for managing internal operations, including jobs, tasks, equipment, and role-based access.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <github-repo-url>
   cd jobops
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the project root with the following:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_NAME=jobops
   DATABASE_USER=your_postgres_username
   DATABASE_PASSWORD=your_postgres_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

4. **Set Up PostgreSQL**:
   - Install PostgreSQL and create a database named `jobops`.
   - Run migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

5. **Run the Server**:
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://localhost:8000`.

