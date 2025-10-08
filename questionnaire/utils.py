from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

file_name = "Questionnaire_Medecine_Naturelle_Interactif.pdf"
c = canvas.Canvas(file_name, pagesize=A4)
width, height = A4
margin = 2*cm
y = height - margin

# Fonction pour écrire un titre de section
def add_section_title(title, y_pos):
    c.setFillColor(colors.green)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y_pos, title)
    return y_pos - 1*cm

# Fonction pour écrire question simple
def add_question(question, y_pos):
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(margin, y_pos, question)
    return y_pos - 0.7*cm

# Fonction pour ajouter cases à cocher interactives
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

# Section 1
y = add_section_title("Section 1 : Informations générales", y)
y = add_question("Nom (facultatif) : ___________________________", y)
y = add_question("Âge : ____ ans", y)
y = add_checkbox("Sexe :", ["Homme", "Femme", "Autre"], y, "gender")
y -= 1*cm
y = add_question("Ville/Région : ___________________________", y)
y = add_question("Profession : ___________________________", y)
y -= 1*cm

# Section 2
y = add_section_title("Section 2 : Connaissance et utilisation", y)
y = add_checkbox("Connaissez-vous la médecine naturelle ?", ["Oui", "Non"], y, "know_natural")
y = add_checkbox("Avez-vous déjà utilisé des plantes médicinales ?", ["Oui, régulièrement", "Oui, parfois", "Non, jamais"], y, "used_plants")
y = add_checkbox("Si oui, pour quels types de soins ?", ["Digestion", "Stress / sommeil", "Vitalité / énergie", "Soins de la peau / cheveux", "Autre: __________"], y, "care_type")
y -= 1*cm

# Section 3
y = add_section_title("Section 3 : Fréquence et préférences", y)
y = add_checkbox("À quelle fréquence utilisez-vous des produits naturels ?", ["Quotidiennement", "Hebdomadairement", "Mensuellement", "Rarement"], y, "frequency")
y = add_checkbox("Où achetez-vous principalement ces produits ?", ["Marchés locaux", "Pharmacies", "Boutiques spécialisées", "En ligne", "Autre: __________"], y, "purchase_place")
y = add_checkbox("Préférez-vous :", ["Produits bruts", "Produits transformés", "Peu importe"], y, "product_type")
y -= 1*cm

# Section 4
y = add_section_title("Section 4 : Motivations et attentes", y)
y = add_checkbox("Quelles sont vos principales motivations ?", ["Prévention santé", "Remèdes alternatifs", "Bien-être général", "Tradition / culture", "Autre: __________"], y, "motivations")
y = add_question("Quels critères sont importants pour l'achat de produits naturels ? ___________________________", y)
y -= 1*cm

# Section 5
y = add_section_title("Section 5 : Intérêt pour les services", y)
y = add_checkbox("Seriez-vous intéressé(e) par :", ["Consultations", "Formations / ateliers", "Abonnements produits naturels", "Conseils personnalisés"], y, "services")
y = add_checkbox("Combien seriez-vous prêt(e) à payer ?", ["< 5 000 FCFA", "5 000 – 10 000 FCFA", "10 000 – 20 000 FCFA", "> 20 000 FCFA"], y, "price")
y -= 1*cm

# Section 6
y = add_section_title("Section 6 : Suggestions", y)
y = add_question("Quels types de produits ou services souhaiteriez-vous voir développés ? ___________________________", y)
y = add_question("Autres commentaires : ___________________________", y)

c.save()
print(f"PDF interactif généré : {file_name}")
