import os
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import dotenv
import openpyxl

# Charger les variables d'environnement depuis le fichier .env
dotenv.load_dotenv()

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DIRECTORY = os.getenv("NLP_DIRECTORY")
SAS_TOKEN = os.getenv("SAS_TOKEN")
OUTPUT_DIR = "nlp_extracted_data"  # Répertoire pour sauvegarder les données extraites

# Fonction pour télécharger et traiter les fichiers dans un dossier et ses sous-dossiers
def download_and_process_files():
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/",
        credential=SAS_TOKEN
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    try:
        # Lister tous les blobs (récursivement) dans le répertoire spécifié
        blobs = container_client.list_blobs(name_starts_with=DIRECTORY)
        for blob in blobs:
            blob_name = blob.name
            print(f"Téléchargement du fichier : {blob_name}")
            blob_client = container_client.get_blob_client(blob_name)
            file_data = blob_client.download_blob().readall()
            process_file(blob_name, file_data)
    except Exception as e:
        print(f"Erreur lors du téléchargement ou du traitement des fichiers : {e}")

# Fonction pour traiter chaque fichier téléchargé
def process_file(file_name, file_data):
    try:
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Déterminer le chemin de sortie relatif au sous-dossier
        relative_path = os.path.relpath(file_name, start=DIRECTORY)
        output_path = os.path.join(OUTPUT_DIR, os.path.dirname(relative_path))
        os.makedirs(output_path, exist_ok=True)

        # Détection du type de fichier
        if file_name.endswith('.csv'):
            # Traiter les fichiers CSV
            print(f"Traitement du fichier CSV : {file_name}")
            csv_data = BytesIO(file_data)
            df = pd.read_csv(csv_data)
            output_file = os.path.join(output_path, os.path.basename(file_name))
            df.to_csv(output_file, index=False)
            print(f"Fichier CSV sauvegardé : {output_file}")

        elif file_name.endswith('.xlsx'):
            # Traiter les fichiers Excel
            print(f"Traitement du fichier Excel : {file_name}")
            xlsx_data = BytesIO(file_data)
            df = pd.read_excel(xlsx_data, engine="openpyxl")
            csv_file_name = os.path.splitext(os.path.basename(file_name))[0] + '.csv'
            output_file = os.path.join(output_path, csv_file_name)
            df.to_csv(output_file, index=False)
            print(f"Fichier Excel converti en CSV et sauvegardé : {output_file}")

        else:
            print(f"Type de fichier non supporté ou ignoré : {file_name}")
    except Exception as e:
        print(f"Erreur lors du traitement du fichier {file_name} : {e}")

# Fonction principale
def main():
    try:
        download_and_process_files()
    except Exception as e:
        print(f"Erreur dans la fonction principale : {e}")

if __name__ == "__main__":
    main()
