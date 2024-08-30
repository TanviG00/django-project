from django.urls import path
from .views import QuestionAnswerAPI

urlpatterns = [
    path('upload/', QuestionAnswerAPI.as_view(), name='file-upload'),
]
