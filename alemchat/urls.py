from django.urls import path
from . import views

urlpatterns = [
    path('start-chat/<int:post_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.chat_room, name='chat_room'),
    path('inbox/', views.inbox, name="inbox"),

    #JSON endpoint
    path('api/chat/<int:chat_id>/send/',views.api_send_message, name='api_send_message'),
    path('api/chat/<int:chat_id>/messages/', views.api_fetch_messages, name='api_fetch_messages'),
    path('api/chat/<int:chat_id>/typing/', views.api_typing_ping, name='api_typing_ping'),
]