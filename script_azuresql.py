import pyodbc
import os
from dotenv import load_dotenv
import csv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les valeurs depuis le .env
db_server = os.getenv('DB_SERVER')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Connexion à la base SQL Server
conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={db_server};'
    f'DATABASE={db_name};'
    f'UID={db_user};'
    f'PWD={db_password}'
)

print("Connexion établie avec succès !")

# Dossier racine pour sauvegarder les fichiers CSV
output_dir = "adventureworks_tables"
os.makedirs(output_dir, exist_ok=True)

# Dictionnaire pour organiser les tables par thème
themes = {
    "Person": "Person",
    "Production": "Production",
    "Sales": "Sales"
}

# Créer les dossiers thématiques si nécessaires
for theme in themes.values():
    os.makedirs(os.path.join(output_dir, theme), exist_ok=True)

# Récupération des noms des tables
try:
    cursor = conn.cursor()
    cursor.execute("""
    SELECT TABLE_SCHEMA, TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA NOT IN ('HumanResources', 'Purchasing', 'dbo');
    """)
    tables = [(row.TABLE_SCHEMA, row.TABLE_NAME) for row in cursor.fetchall()]
    print(f"Tables récupérées : {tables}")
except Exception as e:
    print(f"Erreur lors de la récupération des tables : {e}")
    conn.close()
    exit()

# Exportation des données de chaque table en CSV
for schema_name, table_name in tables:
    print(f"Extraction des tables : {schema_name}, {table_name}")

    # Déterminer le dossier thématique
    theme_dir = None
    for theme, prefix in themes.items():
        if schema_name.lower().startswith(prefix.lower()):  # Vérifie si le schema_name commence par le préfixe
            theme_dir = theme
            break

    if theme_dir:
        # Chemin du dossier thématique
        theme_path = os.path.join(output_dir, theme_dir)
        os.makedirs(theme_path, exist_ok=True)
    else:
        # Si aucun thème ne correspond, ignorer cette table
        print(f"Table ignorée : {schema_name}.{table_name}")
        continue

    try:
        # Préparer la requête pour récupérer les données
        query = f"SELECT * FROM [{schema_name}].[{table_name}];"
        cursor.execute(query)
        
        # Récupérer les colonnes
        columns = [column[0] for column in cursor.description]
        
        # Préparer le fichier CSV
        csv_filename = os.path.join(theme_path, f"{schema_name}_{table_name}.csv")
        with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            
            # Écrire les colonnes en en-tête
            writer.writerow(columns)
            
            # Écrire les données ligne par ligne
            for row in cursor.fetchall():
                writer.writerow(row)
        
        print(f"Table {table_name} sauvegardée dans {csv_filename}")
    except Exception as e:
        print(f"Erreur lors de l'extraction de la table {schema_name}, {table_name} : {e}")

# Fermeture de la connexion
conn.close()
print("Extraction terminée.")


