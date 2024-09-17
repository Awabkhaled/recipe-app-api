"""Views for the recipe APIs"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializers.RecipeDetailsSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Override get query set"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Choose the serializer depending on the action"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Method to create a recipe with the auth user"""
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base view sset for recipe attr"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Viewset for tags that handles endpoints"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Viewsets for ingrediant features"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
