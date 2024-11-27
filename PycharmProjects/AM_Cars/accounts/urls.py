from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('activate/<uid64>/<token>/', views.activate, name='activate'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

]
