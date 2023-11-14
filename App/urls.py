from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:question_id>', views.question, name='question'),
    path('hot', views.hot, name='hot'),
    path('tag/<str:tag_title>', views.tag, name='tag'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('ask', views.ask, name='ask'),
    path('profile', views.profile, name='profile'),
]
