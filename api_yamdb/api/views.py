from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters, mixins, viewsets

from reviews.models import Category, Genre, Review, Title, User
from . filters import TitleFilter
from .permissions import (IsAunthOrReadOnly,
                          IsSuperOrIsAdminOnly,
                          IsSuperIsAdminIsModeratorIsAuthorOnly)
from .serializers import (CategorySerializer,
                          CommentSerializer,
                          GenreSerializer,
                          TitleReadOnlySerializer,
                          ReviewSerializer
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
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))#<<<---Изменил queryset
    permission_classes = (IsAunthOrReadOnly | IsSuperOrIsAdminOnly, )
    serializer_class = TitleReadOnlySerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Review."""
    permission_classes = (
        IsAunthOrReadOnly, IsSuperIsAdminIsModeratorIsAuthorOnly, 
    )
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.OrderingFilter,)
    ordering = ('id',)


    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = (
        IsAunthOrReadOnly, IsSuperIsAdminIsModeratorIsAuthorOnly
    )
    pagination_class = PageNumberPagination
    filter_backends = (filters.OrderingFilter,)
    ordering = ('id',)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
