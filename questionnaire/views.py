import csv
import io
import logging

from django.db import connection
from django.db.models import Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from questionnaire.forms import QuestionnaireForm
from questionnaire.models import ReponseQuestionnaire

# --------------------------------------------------------------------
# 🧩 Configuration du logger
# --------------------------------------------------------------------
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------
# ✅ 1. PAGE D’ACCUEIL
# --------------------------------------------------------------------
def home(request):
    return render(request, 'questionnaire/home.html')


# --------------------------------------------------------------------
# ✅ 2. FORMULAIRE PRINCIPAL
# --------------------------------------------------------------------
def remplir_formulaire(request):
    """
    Vue pour afficher et traiter le formulaire de médecine naturelle.
    Inclut logs détaillés pour diagnostiquer facilement les erreurs.
    """
    logger.info("=== Nouvelle requête sur /remplir/ ===")

    if request.method == "POST":
        form = QuestionnaireForm(request.POST)
        logger.info("Méthode POST reçue, données : %s", request.POST.dict())

        if form.is_valid():
            try:
                form.save()
                logger.info("Formulaire enregistré avec succès ✅")
                return redirect('/merci/')
            except Exception as e:
                logger.exception(f"Erreur lors de form.save() : {e}")
                return render(request, "questionnaire/formulaire.html", {
                    "form": form,
                    "error_message": "Erreur interne lors de l'enregistrement du formulaire."
                })
        else:
            logger.warning("Formulaire invalide ! Erreurs : %s", form.errors)
            return render(request, "questionnaire/formulaire.html", {
                "form": form,
                "error_message": "Le formulaire contient des erreurs. Merci de vérifier vos réponses."
            })
    else:
        form = QuestionnaireForm()
        return render(request, "questionnaire/formulaire.html", {"form": form})


def merci(request):
    """Page de remerciement après soumission"""
    return render(request, 'questionnaire/merci.html')


# --------------------------------------------------------------------
# ✅ 3. EXPORT CSV
# --------------------------------------------------------------------
def export_reponses_csv(request):
    """Exporte les réponses au questionnaire au format CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reponses_questionnaire.csv"'

    writer = csv.writer(response)
    fields = [f.name for f in ReponseQuestionnaire._meta.get_fields() if not f.many_to_many and not f.one_to_many]
    writer.writerow(fields)

    for rep in ReponseQuestionnaire.objects.all():
        writer.writerow([getattr(rep, field, '') for field in fields])

    return response


# --------------------------------------------------------------------
# ✅ 4. DASHBOARD
# --------------------------------------------------------------------
def dashboard(request):
    total_reponses = ReponseQuestionnaire.objects.count()
    moyenne_age = ReponseQuestionnaire.objects.aggregate(Avg('age'))['age__avg'] or 0
    repartition_sexe = ReponseQuestionnaire.objects.values('sexe').annotate(total=Count('sexe'))

    context = {
        'total_reponses': total_reponses,
        'moyenne_age': round(moyenne_age, 1),
        'labels': [r['sexe'] for r in repartition_sexe],
        'data': [r['total'] for r in repartition_sexe],
    }
    return render(request, 'questionnaire/dashboard.html', context)


# --------------------------------------------------------------------
# ✅ 5. LISTE DES RÉPONSES
# --------------------------------------------------------------------
def liste_reponses(request):
    """Affiche toutes les réponses"""
    reponses = ReponseQuestionnaire.objects.all().order_by('-created_at')
    return render(request, 'questionnaire/liste_reponses.html', {'reponses': reponses})


# --------------------------------------------------------------------
# ✅ 6. GÉNÉRATION PDF (questionnaire vierge)
# --------------------------------------------------------------------
def check_page_space(y, c, min_space=5 * cm):
    """Crée une nouvelle page si la zone d'écriture est presque pleine"""
    if y < min_space:
        c.showPage()
        y = 27 * cm
    return y


def generate_pdf(request):
    """Génère un PDF vierge du questionnaire"""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="questionnaire.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

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

    def add_checkbox(question, options, y):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2.5 * cm, y, f"- {question}")
        y -= 0.8 * cm

        c.setFont("Helvetica", 12)
        for opt in options:
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.black)
            c.rect(3 * cm, y - 0.3 * cm, 0.4 * cm, 0.4 * cm, fill=1)
            c.setFillColor(colors.black)
            c.drawString(3.6 * cm, y - 0.2 * cm, opt)
            y -= 0.8 * cm

        return y - 0.3 * cm

    # --- Structure du PDF ---
    y = 27 * cm
    y = add_title("Questionnaire Étude de Marché – Médecine Naturelle au Sénégal", y)

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
    ]

    for title, items in sections:
        y = check_page_space(y, c)
        y = add_section_title(title, y)
        for item in items:
            if isinstance(item, tuple):
                y = add_checkbox(item[0], item[1], y)
            else:
                y = add_question(item, y)
        y -= 0.5 * cm

    c.save()
    return response


# --------------------------------------------------------------------
# ✅ 7. TESTS ET OUTILS TECHNIQUES
# --------------------------------------------------------------------
@csrf_exempt
def test_post(request):
    """Test POST simple pour debug"""
    if request.method == "POST":
        return JsonResponse({"message": "POST reçu", "data": request.POST.dict()})
    return JsonResponse({"message": "GET OK"})


def test_post_form(request):
    """Formulaire test POST"""
    return render(request, "questionnaire/test_post.html")


def test_db_connection(request):
    """Test de connexion à la base"""
    try:
        connection.ensure_connection()
        return HttpResponse("✅ Connexion à la base réussie")
    except Exception as e:
        return HttpResponse(f"❌ Erreur de connexion : {e}")


# --------------------------------------------------------------------
# ✅ 8. PAGES D’ERREUR
# --------------------------------------------------------------------
def custom_404(request, exception):
    return render(request, 'questionnaire/404.html', status=404)


def custom_500(request):
    return render(request, 'questionnaire/500.html', status=500)
