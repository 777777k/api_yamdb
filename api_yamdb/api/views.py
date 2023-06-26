from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .pagination import UsersPagination
from .permissions import (AdminModeratorAuthorPermission,
                          AdminOnly, IsAdminUserOrReadOnly)
from .serializers import (AdminSerializer, CategorySerializer,
                          CommentSerializer, ConfirmationCodeSerializer,
                          GenreSerializer, GetJWTSerializer,
                          ReviewSerializer, TitleReadOnlySerializer,
                          TitleSAFESerializer, UsersSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели User."""
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    pagination_class = UsersPagination
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False, methods=['get', 'patch', 'post'],
        url_path='me', url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def my_profile(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UsersSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(Avg('reviews__score'))
    permission_classes = (IsAdminUserOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSAFESerializer
        return TitleReadOnlySerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_confirmation_code(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username'].lower()
    email = serializer.validated_data['email'].lower()

    user = User.objects.get_or_create(username=username, email=email)[0]

    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Код подтверждения на Yamdb',
        message=(f'Привет, {username.title()}!\n'
                 f'Ваш код подтверждения: {confirmation_code}'),
        from_email=settings.DEFAULT_ADMIN_EMAIL,
        recipient_list=[email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_user(request):
    serializer = GetJWTSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']

    user = get_object_or_404(User, username=username)

    if not default_token_generator.check_token(user, confirmation_code):
        raise serializers.ValidationError(
            {'Ошибка': 'Неверный код подтверждения.'}
        )

    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для обьектов модели Review."""
    permission_classes = (AdminModeratorAuthorPermission,)
    serializer_class = ReviewSerializer
    pagination_class = UsersPagination
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
    permission_classes = (AdminModeratorAuthorPermission,)
    pagination_class = UsersPagination
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
