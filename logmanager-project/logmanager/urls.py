 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import RedirectView

 
from dashboard.views import DashboardView
from users.views import UserRegistrationView, UserProfileView

urlpatterns = [ 
    path('admin/', admin.site.urls), 
    path('', DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', UserRegistrationView.as_view(), name='signup'),
    path('profile/', UserProfileView.as_view(), name='profile'), 
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]

 
urlpatterns += [
     
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
     
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('logs/', include('logs.urls', namespace='logs')), 
    path('notifications/', include('notifications.urls', namespace='web_notifications')),
    path('user-profile/', include('users.urls', namespace='web_users')),
    path('classification/', include('classification.urls')),
     
    path('accounts/profile/', RedirectView.as_view(pattern_name='users:profile'), name='legacy_profile'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 