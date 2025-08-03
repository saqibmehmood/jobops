FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Run migrations, dummy data, and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py generate_dummy_data --jobs 10 && python manage.py runserver 0.0.0.0:8000"]