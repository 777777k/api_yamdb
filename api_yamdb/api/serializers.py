from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Title, Review


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    lookup_field = 'slug'

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""
    lookup_field = 'slug'

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSAFESerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title при SAFE запросах."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title при NOT SAFE запросах."""
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'name',
            'year',
            'description',
            'genre',
            'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if not self.context.get('request').method == 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            'id', 'text', 'author', 'pub_date')


class ConfirmationCodeSerializer(serializers.Serializer):
    """Сериализатор для функции отправки confirmation_code."""
    username = serializers.CharField()
    email = serializers.EmailField()


class GetJWTSerializer(serializers.Serializer):
    """Сериализатор для функции отправки токена пользователю."""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
