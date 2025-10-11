from django.urls import path
from .views import home, merci, test_post_form, test_post
from questionnaire.views import generate_pdf_from_response
from . import views



urlpatterns = [
    path('', home, name='questionnaire'),
    path('generate-pdf/', views.generate_pdf, name='generate-pdf'),
    path('pdf/<int:id>/', views.generate_pdf_from_response, name='generate_pdf_from_response'),
    path('questionnaire/', views.questionnaire_view, name='questionnaire'),
    path('remplir/', views.remplir_formulaire, name='remplir_formulaire'),
    path('merci/', merci, name='merci'),
    path('export-csv/', views.export_reponses_csv, name='export_reponses_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("test-post/", test_post, name="test_post"),
    path("test-post-form/", test_post_form, name="test_post_form"),
]




