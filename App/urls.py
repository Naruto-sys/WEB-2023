from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:question_id>', views.question, name='question'),
    path('hot', views.hot, name='hot'),
    path('tag/<str:tag_title>', views.tag, name='tag'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('ask', views.ask, name='ask'),
    path('profile/edit', views.profile, name='profile'),
    path('end_session', views.end_session, name='end_session'),
    path('question_like/', views.question_like, name='question_like'),
    path('answer_like/', views.answer_like, name='answer_like'),
    path('correct_answer/', views.correct_answer, name='correct_answer')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STAT_ROOT)
