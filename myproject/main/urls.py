from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('products/<int:product_id>/like/', views.LikeProductView.as_view(), name='like-product'),
    path('products/<int:product_id>/favorite/', views.FavoriteProductView.as_view(), name='favorite-product'),
]
