from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from . filters import TitleFilter
from reviews.models import Category, Genre, Title
from .permissions import (IsAunthOrReadOnly,
                          IsSuperOrIsAdminOnly)
# IsSuperIsAdminIsModeratorIsAuthorOnly)
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleReadOnlySerializer
                          )
# TitleSAFESerializer,


class CategoryViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                      mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAunthOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAunthOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    # Наверное необходимо будет изменить queryset после реализации оценок
    queryset = Title.objects.all()
    permission_classes = (IsAunthOrReadOnly | IsSuperOrIsAdminOnly, )
    serializer_class = TitleReadOnlySerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter
