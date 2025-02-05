from rest_framework import serializers
from .models import Category, Product, Comment, Like, Favorite


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Отображаем имя пользователя

    class Meta:
        model = Comment
        fields = ['id', 'user', 'product', 'content', 'rating', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Отображаем имя пользователя

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Отображаем имя пользователя

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    liked_by = LikeSerializer(many=True, read_only=True)
    favorited_by = FavoriteSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'image', 'created_at', 'updated_at',
            'comments', 'liked_by', 'favorited_by'
        ]


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products']
