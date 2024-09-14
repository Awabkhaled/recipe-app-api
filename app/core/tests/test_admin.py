"""Tests that is related to admin"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """testing admin related feature"""
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="adminTest@example.com",
            password="adminTest1234",
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="user1234",
            name='Test user'
        )

    def test_listing_users(self):
        """testing to list users"""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.name)

    def test_change_user_info(self):
        """testing changing user information"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """test if creating user page works"""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code,200)
