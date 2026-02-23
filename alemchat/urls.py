from django.urls import path
from . import views

urlpatterns = [
    path("chats/", views.chats_view, name="chat_list"),
    path("<str:username>/", views.chats_view, name="chat_room"),

    path("ajax/send-message/", views.send_message, name="send_message"),
    path("fetch/<int:chatroom_id>/", views.fetch_messages, name="fetch_messages"),
    path("delete/<int:chat_id>/", views.delete_chat, name="delete_chat"),
    path("block/<int:user_id>/", views.block_user, name="block_user"),


]
