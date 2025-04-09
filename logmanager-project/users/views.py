"""
API views for the users app.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import UserActivity
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserActivitySerializer,
    UserProfileSerializer
)
from .permissions import (
    IsAdmin, 
    IsAdminOrManager, 
    IsOwnerOrAdmin
)
from django.views.generic import CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, UserProfileForm

User = get_user_model()


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    View to display the authenticated user's profile.
    """
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_activities'] = UserActivity.objects.filter(user=self.request.user)[:5]
        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """
    View for editing user profile through the web UI.
    """
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API view for creating new users. Only administrators can register new users.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdmin]


class UserRegistrationView(CreateView):
    """
    View for user registration/signup through the web UI.
    """
    template_name = 'users/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('dashboard')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add placeholders and classes to form widgets
        form.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        form.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
        form.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
        # Add placeholder for email if it exists in the form
        if 'email' in form.fields:
            form.fields['email'].widget.attrs.update({'placeholder': 'Enter email'})
        return form
    
    def form_valid(self, form):
        # Save the user
        response = super().form_valid(form)
        
        # Log the user in
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        
        # Add a success message
        messages.success(self.request, f'Account created for {username}! You are now logged in.')
        
        return response


class UserListView(generics.ListAPIView):
    """
    API view to list all users. Only admins and managers can access this view.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'department']
    ordering_fields = ['username', 'date_joined', 'role']
    ordering = ['username']


class UserDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a user's details. Only admins, managers, or the user themselves can access this.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]


class UserUpdateView(generics.UpdateAPIView):
    """
    API view to update a user's details. Only admins, managers, or the user themselves can update.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrAdmin]


class UserActivityListView(generics.ListAPIView):
    """
    API view to list user activities. Users can see their own activities,
    while admins and managers can see all activities.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'action', 'object_type', 'created_at']
    search_fields = ['action', 'object_type', 'details']
    ordering_fields = ['created_at', 'user', 'action']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=user) 