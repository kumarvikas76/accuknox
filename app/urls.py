from django.urls import path
from .views import signup, login, search_users, list_friends, list_pending_friend_requests, friend_request

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('search-users/', search_users, name='search_users'),
    path('friends/', list_friends, name='list_friends'),
    path('pending-requests/', list_pending_friend_requests, name='list_pending_friend_requests'),
    path('friend-request/',friend_request, name='friend_request'),
]