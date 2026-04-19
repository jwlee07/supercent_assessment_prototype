from django.urls import path
from core import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('ontology/', views.ontology, name='ontology'),
    path('ontology/data/', views.ontology_data, name='ontology_data'),
    path('ask/', views.ask_view, name='ask'),
    path('teams/', views.teams, name='teams'),
    path('upload/', views.upload, name='upload'),
    path('upload/audio/', views.upload_audio, name='upload_audio'),
    path('upload/metrics/', views.upload_metrics, name='upload_metrics'),
    path('upload/marketing/', views.upload_marketing, name='upload_marketing'),
    path('upload/research/', views.upload_research, name='upload_research'),
    path('upload/abtest/', views.upload_abtest, name='upload_abtest'),
    path('api/games/<int:game_id>/graph/', views.game_graph_data, name='game_graph_data'),
]
