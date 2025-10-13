# monquestionnaire/wsgi.py

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Définir la variable d'environnement pour les settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monquestionnaire.settings')

# Charger l'application WSGI Django
application = get_wsgi_application()

# Configurer WhiteNoise pour servir les fichiers statiques
# Le chemin '/app/staticfiles' est utilisé par Railway pour les fichiers statiques
application = WhiteNoise(application, root='/app/staticfiles', prefix='static/')
