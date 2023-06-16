from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from . filters import TitleFilter
from reviews.models import Category, Genre, Title, User
from .permissions import (IsAunthOrReadOnly,
                          IsSuperOrIsAdminOnly)
from .serializers import (CategorySerializer,
                          GenreSerializer,
                          TitleReadOnlySerializer,
                          SignupConfirmationCode,
                          GetJWTUser
                          )


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_confirmation_code(request):
    serializer = SignupConfirmationCode(data=request.data)
    serializer.is_valid(raise_exception=True)
    #  Скорее всего добавление пользователя в базу можно сделать по-другому
    #  Напишите, если есть предложения по оптимизации
    username = request.data.get('username').lower()
    email = request.data.get('email').lower()
    try:
        user = User.objects.get(username=username)
    except Exception:
        user = User.objects.create(username=username, email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Код подтверждения на Yamdb',
        message=(f'Привет, {username.title()}!\n'
                 f'Ваш код подтверждения: {confirmation_code}'),
        from_email='yamdb@yamdb.ru',
        recipient_list=[email],
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_user(request):
    serializer = GetJWTUser(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response({'Ошибка': 'Неверный код подтверждения.'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
