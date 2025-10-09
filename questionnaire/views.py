import csv

from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
import io

from questionnaire.forms import QuestionnaireForm
from questionnaire.models import ReponseQuestionnaire


def generate_pdf_view(request):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 2*cm
    y = height - margin

    # --- Fonctions utilitaires ---
    def add_section_title(title, y_pos):
        c.setFillColor(colors.green)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_pos, title)
        return y_pos - 1*cm

    def add_question(question, y_pos):
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(margin, y_pos, question)
        return y_pos - 0.7*cm

    def add_checkbox(question, options, y_pos, field_prefix):
        y_pos = add_question(question, y_pos)
        c.setFont("Helvetica", 12)
        for i, option in enumerate(options):
            field_name = f"{field_prefix}_{i}"
            c.acroForm.checkbox(
                name=field_name,
                tooltip=option,
                x=margin,
                y=y_pos - 0.2*cm,
                size=12,
                borderStyle='solid',
                borderWidth=1,
                fillColor=colors.white,
                textColor=colors.black,
                buttonStyle='check'
            )
            c.drawString(margin + 0.6*cm, y_pos, option)
            y_pos -= 0.7*cm
        return y_pos

    # --- Création du PDF ---

    # Titre principal
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(margin, y, "Questionnaire Étude de Marché – Médecine Naturelle au Sénégal")
    y -= 1.5*cm

    # Section 1 : Informations générales
    y = add_section_title("Section 1 : Informations générales", y)
    y = add_question("Nom (facultatif) : ___________________________", y)
    y = add_question("Âge : ____ ans", y)
    y = add_checkbox("Sexe :", ["Homme", "Femme", "Autre"], y, "gender")
    y -= 1*cm
    y = add_question("Adresse : ___________________________", y)
    y = add_question("Ville/Région : ___________________________", y)
    y = add_question("Email : ___________________________", y)
    y = add_question("Téléphone : ___________________________", y)
    y = add_question("Profession : ___________________________", y)
    y -= 1*cm

    # Section 2 : Connaissance et utilisation
    y = add_section_title("Section 2 : Connaissance et utilisation", y)
    y = add_checkbox("Connaissez-vous la médecine naturelle ?", ["Oui", "Non"], y, "know_natural")
    y = add_checkbox("Avez-vous déjà utilisé des plantes médicinales ?", ["Oui, régulièrement", "Oui, parfois", "Non, jamais"], y, "used_plants")
    y = add_checkbox("Si oui, pour quels types de soins ?", ["Digestion", "Stress / sommeil", "Vitalité / énergie", "Soins de la peau / cheveux", "Autre: __________"], y, "care_type")
    y -= 1*cm

    # Section 3 : Fréquence et préférences
    y = add_section_title("Section 3 : Fréquence et préférences", y)
    y = add_checkbox("À quelle fréquence utilisez-vous des produits naturels ?", ["Quotidiennement", "Hebdomadairement", "Mensuellement", "Rarement"], y, "frequency")
    y = add_checkbox("Où achetez-vous principalement ces produits ?", ["Marchés locaux", "Pharmacies", "Boutiques spécialisées", "En ligne", "Autre: __________"], y, "purchase_place")
    y = add_checkbox("Préférez-vous :", ["Produits bruts", "Produits transformés", "Peu importe"], y, "product_type")
    y -= 1*cm

    # Section 4 : Motivations et attentes
    y = add_section_title("Section 4 : Motivations et attentes", y)
    y = add_checkbox("Quelles sont vos principales motivations ?", ["Prévention santé", "Remèdes alternatifs", "Bien-être général", "Tradition / culture", "Autre: __________"], y, "motivations")
    y = add_question("Quels critères sont importants pour l'achat de produits naturels ? ___________________________", y)
    y -= 1*cm

    # Section 5 : Intérêt pour les services
    y = add_section_title("Section 5 : Intérêt pour les services", y)
    y = add_checkbox("Seriez-vous intéressé(e) par :", ["Consultations", "Formations / ateliers", "Abonnements produits naturels", "Conseils personnalisés"], y, "services")
    y = add_checkbox("Combien seriez-vous prêt(e) à payer ?", ["< 5 000 FCFA", "5 000 – 10 000 FCFA", "10 000 – 20 000 FCFA", "> 20 000 FCFA"], y, "price")
    y -= 1*cm

    # Section 6 : Suggestions
    y = add_section_title("Section 6 : Suggestions", y)
    y = add_question("Quels types de produits ou services souhaiteriez-vous voir développés ? ___________________________", y)
    y = add_question("Autres commentaires : ___________________________", y)

    c.showPage()
    c.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Questionnaire_Medecine_Naturelle_Interactif.pdf"'
    return response

# --- Vue d'accueil ---
def home(request):
    return render(request, 'questionnaire/home.html')

def remplir_formulaire(request):
    form = QuestionnaireForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('merci')
    return render(request, 'questionnaire/formulaire.html', {'form': form})

# --- Nouvelle vue pour le formulaire et sauvegarde des réponses ---
def questionnaire_view(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            reponse = form.save()  # Sauvegarde dans PostgreSQL
            # On peut générer un PDF spécifique à cette réponse si besoin :
            # generate_pdf_for_response(reponse)
            return redirect('merci')  # page de remerciement après soumission
    else:
        form = QuestionnaireForm()
    return render(request, 'questionnaire/formulaire.html', {'form': form})

def merci(request):
    return render(request, 'questionnaire/merci.html')

def export_reponses_csv(request):
    # Vérifie que seul l’admin peut accéder à cette page (optionnel)
    if not request.user.is_staff:
        return HttpResponse("Accès refusé", status=403)

    # Prépare la réponse HTTP
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reponses_questionnaire.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Nom', 'Âge', 'Sexe', 'Email', 'Profession', 'Réponses...'])

    # Adapte selon ton modèle
    for rep in ReponseQuestionnaire.objects.all():
        writer.writerow([rep.id, rep.created_at, rep.nom, rep.age, rep.sexe, rep.email, rep.profession])

    return response


def dashboard(request):
    # Récupération des données
    total_reponses = ReponseQuestionnaire.objects.count()
    moyenne_age = ReponseQuestionnaire.objects.aggregate(Avg('age'))['age__avg'] or 0

    # Répartition par sexe
    repartition_sexe = ReponseQuestionnaire.objects.values('sexe').annotate(total=Count('sexe'))
    labels = [r['sexe'] for r in repartition_sexe]
    data = [r['total'] for r in repartition_sexe]

    context = {
        'total_reponses': total_reponses,
        'moyenne_age': round(moyenne_age, 1),
        'labels': labels,
        'data': data,
    }
    return render(request, 'questionnaire/dashboard.html', context)

from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'questionnaire/404.html', status=404)

def custom_500(request):
    return render(request, 'questionnaire/500.html', status=500)




