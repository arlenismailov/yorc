from rest_framework import serializers
from .models import Category, Product, Comment, Like, Favorite


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Отображаем имя пользователя

    class Meta:
        model = Comment
        fields = ['id', 'user', 'product', 'content', 'created_at']  # Убрал rating, так как его нет в модели


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Отображаем имя пользователя

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    liked_by = LikeSerializer(many=True, read_only=True)
    favorited_by = FavoriteSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'image', 'created_at', 
                 'comments', 'liked_by', 'favorited_by']  # Добавил все поля


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products']


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
