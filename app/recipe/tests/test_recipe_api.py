"""Tests for recipe endpoints"""
from django.test import TestCase
from core.models import Recipe, Tag
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailsSerializer
)
RECIPES_URL = reverse('recipe:recipe-list')


def create_details_url(recipe_id):
    """Create and return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """ create a recipe"""
    default = {
        'title': 'recipeTestTitle',
        'time_minutes': 5,
        'price': Decimal('5.50'),
        'description': 'Description test',
        'link': 'http://example.com/recipe',
    }
    default.update(params)
    recipe = Recipe.objects.create(user=user, **default)
    return recipe


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


class PublicRecipeTest(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test Auth is required to call API"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTest(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='user1234')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """test only retrieving my recipe"""
        other_user = create_user(email='otherUser@example.com',
                                 password='otherUser1234')
        create_recipe(user=self.user)
        create_recipe(user=other_user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_details(self):
        """Test retrieving recipe details"""
        recipe = create_recipe(user=self.user)
        DETAILS_URL = create_details_url(recipe.id)
        res = self.client.get(DETAILS_URL)
        serializer = RecipeDetailsSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'recipeTestTitle',
            'time_minutes': 5,
            'price': Decimal('5.50'),
            'description': 'Description test',
            'link': 'http://example.com/recipe', }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial updating on recipes"""
        payload = {
            'title': 'updated title'
        }
        recipe = create_recipe(user=self.user)
        URL = create_details_url(recipe.id)
        res = self.client.patch(URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # important
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.description, 'Description test')
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full updating on recipes"""
        recipe = create_recipe(user=self.user)
        payload = {
            'title': 'updatedTitle',
            'time_minutes': 10,
            'price': Decimal('10.20'),
            'description': 'Updated Description test',
            'link': 'http://updatedexample.com/recipe',
        }
        URL = create_details_url(recipe.id)
        res = self.client.put(URL, payload)  # put not post
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():  # remember items()
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_not_changed(self):
        """Test returning error when trying to change user"""
        recipe = create_recipe(user=self.user)
        URL = create_details_url(recipe.id)
        other_user = create_user(email='t@example.com', password='t123456')
        payload = {'user': other_user.id}  # remember id
        self.client.patch(URL, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        recipe = create_recipe(user=self.user)
        URL = create_details_url(recipe.id)
        res = self.client.delete(URL)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_deleting_others_recipe_error(self):
        """Test deleting other's recipes gaves error"""
        other_user = create_user(email='t@example.com', password='t123456')
        recipe = create_recipe(user=other_user)
        URL = create_details_url(recipe.id)
        res = self.client.delete(URL)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with a new tags"""
        payload = {
            'title': 'recipeTestTitle',
            'time_minutes': 5,
            'price': Decimal('5.50'),
            'description': 'Description test',
            'link': 'http://example.com/recipe',
            'tags': [{'name': 'tag1'}, {'name': 'tag2'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']).exists()
            self.assertTrue(exists)

    def test_create_existing_tag(self):
        tag1 = Tag.objects.create(name='tag1', user=self.user)
        payload = {
            'title': 'recipeTestTitle',
            'time_minutes': 5,
            'price': Decimal('5.50'),
            'description': 'Description test',
            'link': 'http://example.com/recipe',
            'tags': [{'name': 'tag1'}, {'name': 'tag2'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                user=self.user,
                name=tag['name']).exists()
            self.assertTrue(exists)

    def test_update_ricepe_with_new_tag(self):
        """test updating the recipe by adding a new tag"""
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'tag1'}]}
        URL = create_details_url(recipe.id)
        res = self.client.patch(URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='tag1')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_ricepe_with_existing_tag(self):
        """test updating the recipe by adding an existing tag"""
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)
        URL = create_details_url(recipe.id)
        payload = {
            'tags': [{'name': 'tag2'}]
        }
        res = self.client.patch(URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag2, recipe.tags.all())
        self.assertNotIn(tag1, recipe.tags.all())
        # test deleting all the tags in the recipe
        payload = {'tags': []}
        res = self.client.patch(URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
