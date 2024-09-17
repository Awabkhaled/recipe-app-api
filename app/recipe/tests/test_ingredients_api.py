"""Tests for Ingredient APIS"""
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from core.models import Ingredient
from recipe.serializers import IngredientSerializer
INGRED_URL = reverse('recipe:ingredient-list')


def create_user(email='test@example.com', password='test1234'):
    """Helper function that create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_Ingred(user, name='salt'):
    """Helper function that create and return an ingredient with a user"""
    return Ingredient.objects.create(user=user, name=name)


def create_detail_URL(id):
    return reverse('recipe:ingredient-detail', args=[id])


class PublicIngredientTests(TestCase):
    """Tests unauthorized operations"""
    def setUp(self):
        self.client = APIClient()

    def test_list_unauth(self):
        res = self.client.get(INGRED_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngrediantTests(TestCase):
    """Test for authorized user"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)  # note the argument

    def test_retrieve_Ingredients(self):
        """Testing listing ingredients for autherized user"""
        create_Ingred(self.user, name='paper')
        create_Ingred(self.user)
        res = self.client.get(INGRED_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        all_ingred = Ingredient.objects.filter(
            user=self.user).order_by('-name')
        serializer = IngredientSerializer(all_ingred, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_list_Ingredient_limited_for_user(self):
        """Test that the ingredients that is returned is only users"""
        other_user = create_user(email='test2@example.com')
        create_Ingred(self.user)
        create_Ingred(other_user, name='paper')
        res = self.client.get(INGRED_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # Note
        all_ingred = Ingredient.objects.filter(
            user=self.user).order_by('-name')
        serializer = IngredientSerializer(all_ingred, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_upgrade_ingredient(self):
        """Test updating the ingredients info"""
        ingred = create_Ingred(user=self.user)
        payload = {
            'name': 'pepper'
        }
        res = self.client.patch(create_detail_URL(ingred.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingred.refresh_from_db()
        self.assertEqual(ingred.name, payload['name'])

    def test_delete_ingredient(self):
        """test deleting ingredients"""
        ingred = create_Ingred(user=self.user)
        res = self.client.delete(create_detail_URL(ingred.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingred.id).exists())
