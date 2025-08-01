FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

COPY . .

# Copy cronjob file and set permissions
COPY cronjob /etc/cron.d/generate_dummy_data
RUN chmod 0644 /etc/cron.d/generate_dummy_data
RUN crontab /etc/cron.d/generate_dummy_data

ENV PYTHONUNBUFFERED=1

# Run migrations, cron, and Django server
CMD ["sh", "-c", "python manage.py migrate && cron && python manage.py runserver 0.0.0.0:8000"]