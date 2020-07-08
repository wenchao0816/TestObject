from django.urls import path
from .views import ScoreView, IndexView

urlpatterns = [
    path('index', IndexView.as_view(), name='sorted'),
    path('', ScoreView.as_view(), name='sorted')
]
