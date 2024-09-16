"""
Test for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PuplicUserAPITest(TestCase):
    """Test the public features of the user API"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_suc(self):
        """test creating a user"""
        payload = {
            'email': 'testUser@example.com',
            'name': 'testUser',
            'password': 'testUser1234'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_exist_user_error(self):
        """Testing error if the user exists"""
        payload = {
            'email': 'testUser@example.com',
            'name': 'testUser',
            'password': 'testUser1234'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Testing error if the password too short"""
        payload = {
            'email': 'testUser@example.com',
            'name': 'testUser',
            'password': 't4'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generating token for user during loggin in"""
        user_details = {
            'email': 'testUser@example.com',
            'name': 'testUser',
            'password': 'testUser1234'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_user_wrong_info(self):
        """Test returning error loggin in if info is false"""
        user_details = {
            'email': 'testUser@example.com',
            'name': 'testUser',
            'password': 'testUser1234'
        }
        create_user(**user_details)

        # password is wrong
        payload = {
            'email': user_details['email'],
            'password': 'testUser123'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # email is wrong
        payload = {
            'email': 'test@example.com',
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # with blank email
        payload = {
            'email': '',
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # with blank password
        payload = {
            'email': user_details['email'],
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauth(self):
        """Test authentication is reqired"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """Test the private features of the user API (reqire auth)"""
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test1234',
            name='testName'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_auth(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
             res.data, {
                    'email': self.user.email,
                    'name': self.user.name,
             }
        )

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_me_not_allowed(self):
        """Test UPDATing the user profile"""
        payload = {
             'name': 'updated name',
             'password': 'newPassword123'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
