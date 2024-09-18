"""
test models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal
from unittest.mock import patch


def create_user():
    """Create and return a new user"""
    user = get_user_model().objects.create_user(email='test@example.com',
                                                password='test1234')
    return user


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

    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test1234',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='recipeTestTitle',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Description test'
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_creating_tag_suc(self):
        """Test creating a tag succeed"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Chinese')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingred(self):
        """Test creating an ingredients"""
        user = create_user()
        ingred = models.Ingredient.objects.create(user=user, name='salt')
        self.assertEqual(str(ingred), ingred.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')
        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
