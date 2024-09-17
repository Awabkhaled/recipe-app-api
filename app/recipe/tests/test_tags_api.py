"""Tests for the tags api"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from core.models import Tag
from django.contrib.auth import get_user_model
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(email='test@example.com', password='test1234'):
    """Helper function that create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_tag(user, name='tagTestName'):
    """Helper function that create and return a tag with a user"""
    return Tag.objects.create(name=name, user=user)


def create_detail_URL(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagsAPITest(TestCase):
    """Test features that do not need authentication for tags"""
    def setUp(self):
        self.client = APIClient()

    def test_list_tag_unauth(self):
        """Testing unauthrized user to list tags error"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITest(TestCase):
    """Test features that need authentication for tags"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Testing listing tags for autherized user"""
        create_tag(user=self.user, name='vegan')
        create_tag(user=self.user, name='chinese')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(serializer.data, res.data)

    def test_tags_limited_to_user(self):
        """Test that the tags that is returned is only users"""
        other_user = create_user(email='anotherUser@example.com')
        create_tag(user=self.user)
        create_tag(user=other_user, name='other tag')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        my_tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(my_tags, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_update_tags(self):
        """Test updating the tags info"""
        tag = create_tag(user=self.user)
        payload = {
            'name': 'updated name'
        }
        res = self.client.patch(create_detail_URL(tag_id=tag.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tags(self):
        """test deleting tags"""
        tag = create_tag(self.user)
        res = self.client.delete(create_detail_URL(tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
