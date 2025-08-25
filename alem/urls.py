"""
URL configuration for alem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),  # or whatever your app is called
    path('', views.homepage, name='homepage'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('check-username/', views.check_username, name='check_username'),
    path('add', views.new_travel, name='new_travel'),
    path('notifications', views.notifiy, name='notification'),
    path('notifications/notread', views.get_unread_notifications, name='get_unread_notifications'),
    path('chat/', include('alemchat.urls')),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('track/<str:pk>/<str:opp>/', views.track_follow, name='track'),
    path('search/flights', views.search, name='search'),
    path('edit/profile', views.edit_profile, name="edit_profile"),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('search/find_users', views.search_user, name='search_user,')
 
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
