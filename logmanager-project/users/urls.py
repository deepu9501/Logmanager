"""
URL patterns for the users app.
"""

from django.urls import path
from . import views

app_name = 'web_users'

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('activities/', views.UserActivityListView.as_view(), name='activities'),
    path('', views.UserListView.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
] 