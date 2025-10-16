import os
import psycopg2
from urllib.parse import quote_plus, urlparse, urlunparse, parse_qs, urlencode
from dotenv import load_dotenv

# Charger les variables du .env
load_dotenv()

# Déterminer l'environnement (local ou Railway)
RAILWAY_ENV = os.environ.get("RAILWAY_ENVIRONMENT", "False") == "True"

if RAILWAY_ENV:
    # Variables Railway
    user = os.environ.get("PROD_DB_USER")
    password = os.environ.get("PROD_DB_PASSWORD")
    host = os.environ.get("PROD_DB_HOST")
    port = os.environ.get("PROD_DB_PORT")
    db_name = os.environ.get("PROD_DB_NAME")
else:
    # Variables locales
    user = os.environ.get("LOCAL_DB_USER")
    password = os.environ.get("LOCAL_DB_PASSWORD")
    host = os.environ.get("LOCAL_DB_HOST")
    port = os.environ.get("LOCAL_DB_PORT")
    db_name = os.environ.get("LOCAL_DB_NAME")

# Vérification
if not all([user, password, host, port, db_name]):
    print("❌ Veuillez remplir toutes les variables nécessaires dans .env")
    exit(1)

# Encodage du mot de passe pour éviter les caractères spéciaux
password_enc = quote_plus(password)

# Reconstitution de DATABASE_URL
DATABASE_URL = f"postgresql://{user}:{password_enc}@{host}:{port}/{db_name}"

# Analyse pour ajuster sslmode
parsed_url = urlparse(DATABASE_URL)
query = parse_qs(parsed_url.query)

if parsed_url.hostname in ["127.0.0.1", "localhost"]:
    query["sslmode"] = ["disable"]  # tunnel local
else:
    query["sslmode"] = ["require"]  # Railway distant

new_query = urlencode(query, doseq=True)
DATABASE_URL_MOD = urlunparse(
    (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment)
)

# Test de connexion
try:
    conn = psycopg2.connect(DATABASE_URL_MOD, options='-c client_encoding=UTF8')
    print("✅ Connexion réussie !")
    conn.close()
except Exception as e:
    print(f"❌ Erreur : {e}")
