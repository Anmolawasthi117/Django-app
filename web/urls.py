from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('place/<int:pk>/', views.place_detail, name='place_detail'),
    path('place/<int:pk>/add_review/', views.add_review, name='add_review'),
]
