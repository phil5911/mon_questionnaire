from django.urls import path
from . import views
from questionnaire.views import generate_pdf_from_response

urlpatterns = [
    # Page d'accueil du questionnaire
    path('', views.home, name='questionnaire'),

    # Formulaire principal
    path('questionnaire/', views.questionnaire_view, name='questionnaire_view'),
    # path('questionnaire/submit/', views.remplir_formulaire, name='questionnaire_submit'),
    path('remplir/', views.remplir_formulaire, name='remplir_formulaire'),

    # Page de remerciement après soumission
    path('merci/', views.merci, name='merci'),

    # PDF et export CSV
    path('generate-pdf/', views.generate_pdf, name='generate-pdf'),
    path('pdf/<int:id>/', generate_pdf_from_response, name='generate_pdf_from_response'),
    path('export-csv/', views.export_reponses_csv, name='export_reponses_csv'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Test POST
    path('test-post/', views.test_post, name='test_post'),
    path('test-post-form/', views.test_post_form, name='test_post_form'),

    # Liste des réponses
    path('liste-reponses/', views.liste_reponses, name='liste_reponses'),
]



