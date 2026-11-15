from django.urls import path

from w2p2_app.views import (
    bookmark_album,
    delete_bookmarked_album,
    index,
    login,
    logout,
    set_vulnerable,
)

urlpatterns = [
    path('', index, name='index'),
    path('set_vulnerable/', set_vulnerable, name='set_vulnerable'),
    # Login, Logout
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    # Albums
    path('bookmark_album/', bookmark_album, name='bookmark_album'),
    path(
        'delete_bookmarked_album/<int:id>/', delete_bookmarked_album, name='delete_bookmarked_album'
    ),
]
