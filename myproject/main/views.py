from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from .models import Category, Product, Favorite, Like, Comment
from .serializers import CategorySerializer, ProductSerializer, CommentSerializer, FavoriteSerializer, RequestPasswordResetSerializer, PasswordResetConfirmSerializer
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
import logging
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db.models import Q
from django.db.models import Prefetch
from django.db.models import Count
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger('main')

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.NumberFilter(field_name="category__id")
    search = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'search']


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return Comment.objects.filter(product_id=product_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        # Автоматически устанавливаем текущего пользователя
        serializer.save(user=self.request.user)


class LikeProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        like, created = Like.objects.get_or_create(user=request.user, product=product)
        if not created:
            like.delete()
            return Response({'message': 'Like removed'}, status=200)
        return Response({'message': 'Liked'}, status=201)


class FavoriteProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            favorite.delete()
            return Response({'message': 'Removed from favorites'}, status=200)
        return Response({'message': 'Added to favorites'}, status=201)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Оптимизированный queryset с использованием:
        - select_related для ForeignKey (category)
        - prefetch_related для ManyToMany и обратных связей
        """
        queryset = Product.objects.select_related('category').prefetch_related(
            'comments__user',  # Предзагружаем комментарии и их авторов
            'liked_by__user',  # Предзагружаем лайки и их авторов
            Prefetch(
                'favorited_by',
                queryset=Favorite.objects.select_related('user')
            )
        )

        # Добавляем аннотации для подсчета
        queryset = queryset.annotate(
            comments_count=Count('comments'),
            likes_count=Count('liked_by'),
            favorites_count=Count('favorited_by')
        )

        return queryset

    def list(self, request, *args, **kwargs):
        """Оптимизированный список продуктов"""
        queryset = self.get_queryset()
        
        # Фильтрация
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)

        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        if price_min and price_max:
            queryset = queryset.filter(price__range=(price_min, price_max))

        # Поиск
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Оптимизированное получение деталей продукта"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Добавляем похожие товары с оптимизацией
        similar_products = self.get_similar_products(instance)
        similar_serializer = self.get_serializer(similar_products, many=True)
        data['similar_products'] = similar_serializer.data

        return Response(data)

    def create(self, request, *args, **kwargs):
        logger.info(f'User {request.user} creating new product')
        response = super().create(request, *args, **kwargs)
        # Инвалидируем кэш после создания
        cache.delete_pattern('product_queryset_*')
        return response

    def update(self, request, *args, **kwargs):
        logger.info(f'User {request.user} updating product {kwargs.get("pk")}')
        response = super().update(request, *args, **kwargs)
        # Инвалидируем кэш после обновления
        cache.delete_pattern('product_queryset_*')
        return response

    def destroy(self, request, *args, **kwargs):
        logger.info(f'User {request.user} deleting product {kwargs.get("pk")}')
        response = super().destroy(request, *args, **kwargs)
        # Инвалидируем кэш после удаления
        cache.delete_pattern('product_queryset_*')
        return response

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def add_to_favorites(self, request, pk=None):
        logger.info(f'User {request.user} adding product {pk} to favorites')
        product = self.get_object()
        user = request.user
        
        if Favorite.objects.filter(user=user, product=product).exists():
            logger.warning(f'Product {pk} already in favorites for user {user}')
            return Response(
                {"detail": "Продукт уже в избранном"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Favorite.objects.create(user=user, product=product)
        logger.info(f'Product {pk} added to favorites for user {user}')
        # Инвалидируем кэш избранного
        cache.delete(f'user_favorites_{user.id}')
        return Response(
            {"detail": "Продукт добавлен в избранное"}, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def remove_from_favorites(self, request, pk=None):
        logger.info(f'User {request.user} removing product {pk} from favorites')
        product = self.get_object()
        user = request.user
        
        favorite = Favorite.objects.filter(user=user, product=product).first()
        if favorite:
            favorite.delete()
            logger.info(f'Product {pk} removed from favorites for user {user}')
            # Инвалидируем кэш избранного
            cache.delete(f'user_favorites_{user.id}')
            return Response(
                {"detail": "Продукт удален из избранного"}, 
                status=status.HTTP_200_OK
            )
        
        logger.warning(f'Product {pk} not found in favorites for user {user}')
        return Response(
            {"detail": "Продукт не найден в избранном"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        user = request.user
        logger.info(f'User {user} requesting favorites list')
        
        # Пытаемся получить из кэша
        cache_key = f'user_favorites_{user.id}'
        favorites = cache.get(cache_key)
        
        if favorites is None:
            favorites = Favorite.objects.filter(user=user)
            serializer = FavoriteSerializer(favorites, many=True)
            # Кэшируем результат
            cache.set(cache_key, serializer.data, settings.CACHE_TTL)
            logger.info(f'Favorites cached for user {user}')
            return Response(serializer.data)
        
        logger.info(f'Favorites retrieved from cache for user {user}')
        return Response(favorites)

    def get_similar_products(self, product, limit=5):
        """Получение похожих товаров"""
        cache_key = f'similar_products_{product.id}'
        similar_products = cache.get(cache_key)

        if similar_products is None:
            logger.info(f'Calculating similar products for product {product.id}')
            
            # Определяем ценовой диапазон (±30% от цены текущего товара)
            min_price = float(product.price) * 0.7
            max_price = float(product.price) * 1.3

            # Ищем похожие товары
            similar_products = Product.objects.filter(
                Q(category=product.category) |  # Та же категория
                Q(price__range=(min_price, max_price))  # Похожая цена
            ).exclude(
                id=product.id  # Исключаем текущий товар
            ).distinct()[:limit]

            # Кэшируем результат
            cache.set(cache_key, similar_products, settings.CACHE_TTL)
            logger.info(f'Similar products cached for product {product.id}')

        return similar_products

class RequestPasswordResetView(APIView):
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Генерируем токен
                token = default_token_generator.make_token(user)
                
                # Формируем ссылку для сброса
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                
                # Отправляем email
                send_mail(
                    'Восстановление пароля',
                    f'Для сброса пароля перейдите по ссылке: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                logger.info(f"Password reset email sent to {email}")
                return Response(
                    {"detail": "Инструкции по восстановлению пароля отправлены на email"},
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                logger.warning(f"Password reset attempted for non-existent email: {email}")
                return Response(
                    {"detail": "Инструкции по восстановлению пароля отправлены на email"},
                    status=status.HTTP_200_OK
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=request.data.get('email'))
                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    
                    logger.info(f"Password successfully reset for user {user.email}")
                    return Response(
                        {"detail": "Пароль успешно изменен"},
                        status=status.HTTP_200_OK
                    )
                else:
                    logger.warning(f"Invalid password reset token used for {user.email}")
                    return Response(
                        {"detail": "Недействительный токен"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except User.DoesNotExist:
                logger.warning("Password reset attempted with invalid token")
                return Response(
                    {"detail": "Недействительный токен"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
