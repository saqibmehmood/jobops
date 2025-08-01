from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import User, Equipment, Job, JobTask
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generates dummy data for testing JobOps flows'

    def add_arguments(self, parser):
        parser.add_argument('--jobs', type=int, default=10, help='Number of jobs to create')

    def handle(self, *args, **options):
        num_jobs = options['jobs']
        self.stdout.write(self.style.SUCCESS('Generating dummy data...'))

        # Create users
        if not User.objects.filter(username='admin1').exists():
            admin = User.objects.create_superuser(
                username='admin1', email='admin1@example.com', password='admin123', role='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.username}'))
        else:
            admin = User.objects.get(username='admin1')

        technicians = []
        for i in range(1, 3):
            username = f'tech{i}'
            if not User.objects.filter(username=username).exists():
                tech = User.objects.create_user(
                    username=username, email=f'{username}@example.com',
                    password=f'tech{i}123', role='TECHNICIAN'
                )
                technicians.append(tech)
                self.stdout.write(self.style.SUCCESS(f'Created technician: {username}'))
            else:
                technicians.append(User.objects.get(username=username))

        sales_agents = []
        for i in range(1, 3):
            username = f'sales{i}'
            if not User.objects.filter(username=username).exists():
                sales = User.objects.create_user(
                    username=username, email=f'{username}@example.com',
                    password=f'sales{i}123', role='SALES_AGENT'
                )
                sales_agents.append(sales)
                self.stdout.write(self.style.SUCCESS(f'Created sales agent: {username}'))
            else:
                sales_agents.append(User.objects.get(username=username))

        # Create equipment
        equipment_data = [
            {'name': 'Drill', 'type': 'TOOL', 'serial_number': 'DR123'},
            {'name': 'Hammer', 'type': 'TOOL', 'serial_number': 'HM456'},
            {'name': 'Wrench', 'type': 'TOOL', 'serial_number': 'WR789'},
            {'name': 'Crane', 'type': 'MACHINE', 'serial_number': 'CR101'},
            {'name': 'Truck', 'type': 'VEHICLE', 'serial_number': 'TR202'},
        ]
        equipment = []
        for eq in equipment_data:
            if not Equipment.objects.filter(serial_number=eq['serial_number']).exists():
                eq_obj = Equipment.objects.create(**eq, is_active=True)
                equipment.append(eq_obj)
                self.stdout.write(self.style.SUCCESS(f'Created equipment: {eq_obj.name}'))
            else:
                equipment.append(Equipment.objects.get(serial_number=eq['serial_number']))

        # Create jobs
        job_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED']
        priorities = ['LOW', 'MEDIUM', 'HIGH']
        now = timezone.now()
        for i in range(num_jobs):
            scheduled_date = now + timedelta(days=random.randint(-10, 10))  # Past and future for overdue testing
            job = Job.objects.create(
                title=f'Job {i+1}',
                description=f'Description for Job {i+1}',
                client_name=f'Client {i+1}',
                created_by=random.choice(sales_agents),
                assigned_to=random.choice(technicians),
                status=random.choice(job_statuses),
                priority=random.choice(priorities),
                scheduled_date=scheduled_date
            )
            self.stdout.write(self.style.SUCCESS(f'Created job: {job.title}'))

            # Create tasks for each job
            num_tasks = random.randint(2, 5)
            for j in range(num_tasks):
                task = JobTask.objects.create(
                    job=job,
                    title=f'Task {j+1} for Job {i+1}',
                    description=f'Description for Task {j+1}',
                    status=random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED']),
                    order=j+1
                )
                task.required_equipment.set(random.sample(equipment, random.randint(1, 3)))
                self.stdout.write(self.style.SUCCESS(f'Created task: {task.title}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully generated {num_jobs} jobs with tasks.'))