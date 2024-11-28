import os
import zipfile
import tarfile
import pandas as pd
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import dotenv

# Charger les variables d'environnement depuis le fichier .env
dotenv.load_dotenv(override=True)

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DIRECTORY = os.getenv("ZIP_DIRECTORY")
SAS_TOKEN = os.getenv("SAS_TOKEN")
OUTPUT_DIR = "data_zip"  # Dossier local pour sauvegarder les fichiers extraits
TGZ_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "from_tgz")  # Dossier pour les fichiers extraits du TGZ

# Fonction pour télécharger le fichier compressé depuis le data lake
def download_zip_file():
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/",
        credential=SAS_TOKEN
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_name = f"{DIRECTORY}/reviews.zip"
    
    try:
        blob_client = container_client.get_blob_client(blob_name)
        print(f"Téléchargement du fichier : {blob_name}")
        zip_data = blob_client.download_blob().readall()
        return zip_data
    except Exception as e:
        print(f"Erreur lors du téléchargement du fichier ZIP : {e}")
        return None

# Fonction pour traiter les fichiers TGZ
def process_tgz_file(tgz_data):
    try:
        with tarfile.open(fileobj=BytesIO(tgz_data), mode="r:gz") as tgz:
            csv_files = [member for member in tgz.getmembers() if member.name.endswith(".csv")]

            # Assurez-vous que le dossier de sortie pour les fichiers TGZ existe
            os.makedirs(TGZ_OUTPUT_DIR, exist_ok=True)

            # Extraire les fichiers CSV
            for csv_file in csv_files:
                print(f"Extraction du fichier CSV depuis TGZ : {csv_file.name}")
                with tgz.extractfile(csv_file) as f:
                    df = pd.read_csv(f)
                    output_file = os.path.join(TGZ_OUTPUT_DIR, os.path.basename(csv_file.name))
                    df.to_csv(output_file, index=False)
                    print(f"Fichier CSV extrait du TGZ sauvegardé : {output_file}")
    except Exception as e:
        print(f"Erreur lors du traitement du fichier TGZ : {e}")

# Fonction pour traiter le fichier ZIP
def process_zip_file(zip_data):
    try:
        # Lire le fichier ZIP en mémoire
        with zipfile.ZipFile(BytesIO(zip_data)) as z:
            all_files = [file for file in z.namelist()]
            csv_files = [file for file in all_files if file.endswith('.csv')]
            xlsx_files = [file for file in all_files if file.endswith('.xlsx')]
            tgz_files = [file for file in all_files if file.endswith('.tgz')]

            # Assurez-vous que le dossier de sortie existe
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            # Traitement des fichiers CSV
            for csv_file in csv_files:
                print(f"Traitement du fichier CSV : {csv_file}")
                with z.open(csv_file) as f:
                    df = pd.read_csv(f)
                    output_file = os.path.join(OUTPUT_DIR, csv_file)
                    df.to_csv(output_file, index=False)
                    print(f"Fichier CSV sauvegardé : {output_file}")

            # Traitement des fichiers Excel
            for xlsx_file in xlsx_files:
                print(f"Traitement du fichier Excel : {xlsx_file}")
                with z.open(xlsx_file) as f:
                    df = pd.read_excel(f)
                    csv_file_name = os.path.splitext(xlsx_file)[0] + ".csv"
                    output_file = os.path.join(OUTPUT_DIR, csv_file_name)
                    df.to_csv(output_file, index=False)
                    print(f"Fichier Excel converti et sauvegardé en CSV : {output_file}")

            # Traitement des fichiers TGZ
            for tgz_file in tgz_files:
                print(f"Traitement du fichier TGZ : {tgz_file}")
                with z.open(tgz_file) as f:
                    tgz_data = f.read()
                    process_tgz_file(tgz_data)

    except Exception as e:
        print(f"Erreur lors du traitement du fichier ZIP : {e}")

# Fonction principale
def main():
    try:
        # Télécharger le fichier ZIP
        zip_data = download_zip_file()
        if zip_data:
            # Traiter le fichier ZIP
            process_zip_file(zip_data)
    except Exception as e:
        print(f"Erreur dans la fonction principale : {e}")

if __name__ == "__main__":
    main()
