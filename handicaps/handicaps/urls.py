"""handicaps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from caps import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_user, name="logout"),
    path('admin/', admin.site.urls),
    path("register/", views.register_request, name="register"),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
         name='password_reset_complete'),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('okee_upload/', views.okee_upload_view, name='okee_upload'),
    path('okee_get_handicap/', views.okee_get_handicap, name='okee_get_handicap'),
    path('commons_upload/', views.commons_upload_view, name='commons_upload'),
    path('commons_get_handicap/', views.commons_get_handicap, name='commons_get_handicap'),
    path('delray_upload/', views.delray_upload_view, name='delray_upload'),
    path('delray_get_handicap/', views.delray_get_handicap, name='delray_get_handicap'),
    path('pga_upload/', views.pga_upload_view, name='pga_upload'),
    path('pga_get_handicap/', views.pga_get_handicap, name='pga_get_handicap'),
    path('dreher_upload/', views.dreher_upload_view, name='dreher_upload'),
    path('dreher_get_handicap/', views.dreher_get_handicap, name='dreher_get_handicap'),
]
