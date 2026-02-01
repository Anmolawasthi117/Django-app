from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import RegisterView, AddReviewView, PlaceSearchView, PlaceDetailView

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App Logic
    path('reviews/add/', AddReviewView.as_view(), name='add_review'),
    path('places/search/', PlaceSearchView.as_view(), name='search_places'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place_detail'),
]