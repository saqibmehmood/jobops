from django.test import TestCase
from core.models import User


class UserModelTest(TestCase):
    def test_create_admin_user(self):
        # Create a dummy Admin user
        admin = User.objects.create_user(
            username='testadmin',
            email='testadmin@example.com',
            password='test12345',
            role='ADMIN'
        )

        # Verify user attributes
        self.assertEqual(admin.username, 'testadmin')
        self.assertEqual(admin.email, 'testadmin@example.com')
        self.assertEqual(admin.role, 'ADMIN')
        self.assertTrue(admin.check_password('test12345'))
        self.assertTrue(admin.is_active)