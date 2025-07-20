from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('board/<slug:slug>/', views.board_detail, name='board_detail'),
    path('board/<slug:slug>/fetch_updates/', views.fetch_updates, name='fetch_updates'),
    path('access/<slug:slug>/', views.pass_check, name='pass_check'),
    path('create/', views.create_board, name='create_board'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
