from celery import shared_task
from django.utils import timezone
from .models import Job

@shared_task
def flag_overdue_jobs():
    now = timezone.now()
    overdue_jobs = Job.objects.filter(
        scheduled_date__lt=now,
        status__in=['PENDING', 'IN_PROGRESS'],
        overdue=False
    )
    count = overdue_jobs.update(overdue=True)
    return f"Flagged {count} jobs as overdue."