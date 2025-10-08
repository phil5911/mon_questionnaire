from django.urls import path
from .views import generate_pdf_view, home, merci
from . import views

urlpatterns = [
    path('generate-pdf/', generate_pdf_view, name='generate-pdf'),
    path('', home, name='questionnaire'),
    path('questionnaire/', views.questionnaire_view, name='questionnaire'),
    path('remplir/', views.remplir_formulaire, name='remplir_formulaire'),
    path('merci/', merci, name='merci'),
    path('export-csv/', views.export_reponses_csv, name='export-csv'),
    path('dashboard/', views.dashboard, name='dashboard'),

]

