from django.db import models

class ReponseQuestionnaire(models.Model):
    # Section 1 : Informations générales
    nom = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    sexe_choices = [
        ('Homme', 'Homme'),
        ('Femme', 'Femme'),
        ('Autre', 'Autre'),
    ]
    sexe = models.CharField(max_length=10, choices=sexe_choices, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)

    # Section 2 : Connaissance et utilisation
    connait_med_naturelle = models.BooleanField(default=False)
    utilise_plantes = models.CharField(
        max_length=50,
        choices=[
            ('Regulierement', 'Oui, régulièrement'),
            ('Parfois', 'Oui, parfois'),
            ('Jamais', 'Non, jamais')
        ],
        blank=True
    )
    types_soins = models.TextField(blank=True)

    # Section 3 : Fréquence et préférences
    frequence = models.CharField(
        max_length=20,
        choices=[
            ('Quotidien', 'Quotidiennement'),
            ('Hebdomadaire', 'Hebdomadairement'),
            ('Mensuel', 'Mensuellement'),
            ('Rarement', 'Rarement')
        ],
        blank=True
    )
    lieu_achat = models.TextField(blank=True)
    type_produit = models.CharField(
        max_length=20,
        choices=[
            ('Bruts', 'Produits bruts'),
            ('Transformes', 'Produits transformés'),
            ('Peuimporte', 'Peu importe')
        ],
        blank=True
    )

    # Section 4 : Motivations et attentes
    motivations = models.TextField(blank=True)
    criteres_achat = models.TextField(blank=True)

    # Section 5 : Intérêt pour les services
    interet_services = models.TextField(blank=True)
    montant_pret = models.CharField(
        max_length=20,
        choices=[
            ('<5000', '< 5 000 FCFA'),
            ('5000-10000', '5 000 – 10 000 FCFA'),
            ('10000-20000', '10 000 – 20 000 FCFA'),
            ('>20000', '> 20 000 FCFA')
        ],
        blank=True
    )

    # Section 6 : Suggestions
    suggestions = models.TextField(blank=True)
    commentaires = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.ville} ({self.created_at.date()})"
from django.db import models

# Create your models here.
