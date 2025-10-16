import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg.connect(DATABASE_URL)
    print("✅ Connexion réussie !")
    conn.close()
except Exception as e:
    print(f"❌ Erreur : {e}")
