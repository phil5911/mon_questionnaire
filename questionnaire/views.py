import csv
import io
import logging


from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from questionnaire.forms import QuestionnaireForm
from questionnaire.models import ReponseQuestionnaire





# --------------------------------------------------------------------
# ✅ 1. PDF INTERACTIF (vierge à remplir)
# --------------------------------------------------------------------
def check_page_space(y, c, min_space=5 * cm):
    """Crée une nouvelle page si la zone d'écriture est presque pleine"""
    if y < min_space:
        c.showPage()
        y = 27 * cm
    return y

def generate_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="questionnaire.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Fonctions utilitaires ---
    def add_title(title, y):
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.darkblue)
        c.drawString(2 * cm, y, title)
        return y - 1.5 * cm

    def add_section_title(title, y):
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.green)
        c.drawString(2 * cm, y, title)
        return y - 1 * cm

    def add_question(question, y):
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(2.5 * cm, y, f"- {question}")
        return y - 1 * cm

    def add_checkbox(question, options, y, group_name):
        # Question
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(2.5 * cm, y, f"- {question}")
        y -= 0.8 * cm

        # Options
        c.setFont("Helvetica", 12)
        for opt in options:
            # Case blanche avec bord noir
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.black)
            c.rect(3 * cm, y - 0.3 * cm, 0.4 * cm, 0.4 * cm, fill=1)
            # Texte option en noir
            c.setFillColor(colors.black)
            c.drawString(3.6 * cm, y - 0.2 * cm, opt)
            y -= 0.8 * cm

        return y - 0.3 * cm

    # --- Construction du PDF ---
    y = 27 * cm
    y = add_title("Questionnaire Étude de Marché – Médecine Naturelle au Sénégal", y)

    # Sections
    sections = [
        ("Section 1 : Informations générales", [
            "Nom : ___________________________",
            "Âge : ___________________________",
            "Sexe : ___________________________",
            "Profession : ___________________________"
        ]),
        ("Section 2 : Habitudes de consommation", [
            ("Achetez-vous régulièrement des produits naturels ?", ["Oui", "Non"]),
            ("Si oui, où les achetez-vous ?", ["Pharmacie", "Marché", "En ligne", "Autre"]),
            "Quels types de produits naturels consommez-vous ? ___________________________"
        ]),
        ("Section 3 : Connaissance des produits naturels", [
            ("Connaissez-vous la différence entre produits naturels et bios ?", ["Oui", "Non"]),
            ("Comment avez-vous entendu parler des produits naturels ?", ["Internet", "Amis", "TV / Radio", "Autre"])
        ]),
        ("Section 4 : Motivations et attentes", [
            ("Quelles sont vos principales motivations ?", ["Prévention santé", "Remèdes alternatifs", "Bien-être général", "Tradition / culture", "Autre: __________"]),
            "Quels critères sont importants pour l'achat de produits naturels ? ___________________________"
        ]),
        ("Section 5 : Intérêt pour les services", [
            ("Seriez-vous intéressé(e) par :", ["Consultations", "Formations / ateliers", "Abonnements produits naturels", "Conseils personnalisés"]),
            ("Combien seriez-vous prêt(e) à payer ?", ["< 5 000 FCFA", "5 000 – 10 000 FCFA", "10 000 – 20 000 FCFA", "> 20 000 FCFA"])
        ]),
        ("Section 6 : Suggestions", [
            "Quels types de produits ou services souhaiteriez-vous voir développés ? ___________________________",
            "Autres commentaires : ___________________________"
        ]),
    ]

    for title, items in sections:
        y = check_page_space(y, c)
        y = add_section_title(title, y)
        for item in items:
            if isinstance(item, tuple):
                y = add_checkbox(item[0], item[1], y, "")
            else:
                y = add_question(item, y)
        y -= 0.5 * cm

    # Sauvegarde PDF
    c.showPage()
    c.save()
    return response

# --------------------------------------------------------------------
# ✅ 2. PDF AVEC LES RÉPONSES D'UN UTILISATEUR
# --------------------------------------------------------------------
def generate_pdf_from_response(request, id):
    reponse = get_object_or_404(ReponseQuestionnaire, id=id)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Réponses au Questionnaire - Médecine Naturelle")
    y -= 1.5 * cm

    c.setFont("Helvetica", 12)
    for field in reponse._meta.get_fields():
        if field.many_to_many or field.one_to_many:
            continue
        name = field.verbose_name.capitalize()
        value = getattr(reponse, field.name, '')
        c.drawString(margin, y, f"{name} : {value}")
        y -= 0.6 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 12)

    c.showPage()
    c.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reponse_{id}.pdf"'
    return response


# --------------------------------------------------------------------
# ✅ 3. AUTRES VUES (formulaire, export, dashboard)
# --------------------------------------------------------------------
def home(request):
    return render(request, 'questionnaire/home.html')


# Configure le logger
logger = logging.getLogger(__name__)
import logging
from django.shortcuts import render, redirect
from .forms import QuestionnaireForm

logger = logging.getLogger(__name__)

def remplir_formulaire(request):
    """
    Vue pour afficher et traiter le formulaire de médecine naturelle.
    Ajout de logs détaillés pour comprendre les erreurs en production.
    """
    logger.info("=== Nouvelle requête sur /remplir/ ===")

    if request.method == "POST":
        logger.info("Méthode POST reçue, tentative de sauvegarde du formulaire.")
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            try:
                logger.info("Formulaire valide, tentative de sauvegarde en base.")
                form.save()
                logger.info("Formulaire enregistré avec succès ✅")
                return redirect('merci')
            except Exception as e:
                logger.exception(f"Erreur lors de form.save() : {e}")
                return render(request, "formulaire.html", {
                    "form": form,
                    "error_message": "Une erreur interne est survenue lors de l'enregistrement du formulaire."
                })
        else:
            logger.warning(f"Formulaire invalide : {form.errors}")
            return render(request, "formulaire.html", {
                "form": form,
                "error_message": "Le formulaire contient des erreurs. Merci de vérifier vos réponses."
            })
    else:
        logger.info("Méthode GET — affichage du formulaire.")
        form = QuestionnaireForm()
        logger.info("Formulaire servi à jour ✅")
        return render(request, "formulaire.html", {"form": form})

def questionnaire_view(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('merci')
    else:
        form = QuestionnaireForm()
    return render(request, 'questionnaire/formulaire.html', {'form': form})

def merci(request):
    return render(request, 'questionnaire/merci.html')

def export_reponses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reponses_questionnaire.csv"'

    writer = csv.writer(response)
    fields = [f.name for f in ReponseQuestionnaire._meta.get_fields() if not f.many_to_many and not f.one_to_many]
    writer.writerow(fields)

    for rep in ReponseQuestionnaire.objects.all():
        row = [getattr(rep, field, '') for field in fields]
        writer.writerow(row)

    return response

def dashboard(request):
    total_reponses = ReponseQuestionnaire.objects.count()
    moyenne_age = ReponseQuestionnaire.objects.aggregate(Avg('age'))['age__avg'] or 0
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


# --------------------------------------------------------------------
# ✅ 4. ERREURS PERSONNALISÉES
# --------------------------------------------------------------------
def custom_404(request, exception):
    return render(request, 'questionnaire/404.html', status=404)

def custom_500(request):
    return render(request, 'questionnaire/500.html', status=500)






