"""
test models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """test models"""

    def test_create_user_with_email(self):
        """test creating user with email"""
        email = 'test@gmail.com'
        password = 'test1234'
        user = get_user_model().objects.\
            create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password, password)

    def test_new_user_email_norm(self):
        """test email normalized fr users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_no_email_error(self):
        """a user without email is error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_super_user(self):
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            password='test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
