import os
import pandas as pd
import pyarrow.parquet as pq
from azure.storage.blob import BlobServiceClient
import requests
import dotenv

# Charger les variables d'environnement depuis le fichier .env
dotenv.load_dotenv(override=True)

# Configuration
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DIRECTORY = os.getenv("DIRECTORY")
SAS_TOKEN = os.getenv("SAS_TOKEN")  # Lire le SAS token depuis .env
print(SAS_TOKEN)

# Fonction pour télécharger un blob en recréant la structure des répertoires
def download_blob(blob_url, blob_name):
    local_path = os.path.join("parquet_file_tocsv", blob_name)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    response = requests.get(blob_url)
    if response.status_code == 200:
        with open(local_path, "wb") as file:
            file.write(response.content)
        print(f"Fichier téléchargé : {local_path}")
        return local_path
    else:
        print(f"Échec du téléchargement pour {blob_url}, code HTTP : {response.status_code}")
        return None

# Fonction pour télécharger les fichiers Parquet et renvoyer leurs chemins locaux
def download_parquet_files():
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/",
        credential=SAS_TOKEN
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blobs = container_client.list_blobs(name_starts_with=DIRECTORY)

    local_files = []
    for blob in blobs:
        if blob.name.endswith(".parquet"):
            blob_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob.name}?{SAS_TOKEN}"
            print(f"Téléchargement du fichier : {blob.name}")
            local_file = download_blob(blob_url, blob.name)
            if local_file:
                local_files.append(local_file)
    return local_files

# Fonction pour traiter un fichier Parquet : extraction des images et sauvegarde du reste des données
def process_parquet_file(parquet_file, csv_output_dir, image_output_dir):
    try:
        table = pq.read_table(parquet_file)
        df = table.to_pandas()

        images_dir = os.path.join(image_output_dir, os.path.basename(parquet_file).replace(".parquet", ""))
        os.makedirs(images_dir, exist_ok=True)

        # Liste pour stocker les données restantes avec un lien vers les images
        processed_data = []

        for index, row in df.iterrows():
            image_path = None  # Par défaut, aucune image

            if "image" in row:
                content = row["image"]

                if isinstance(content, dict):
                    for key, value in content.items():
                        if isinstance(value, bytes):
                            # Sauvegarder l'image
                            image_path = os.path.join(images_dir, f"image_{index}.png")
                            with open(image_path, "wb") as img_file:
                                img_file.write(value)
                            print(f"Ligne {index}: Image sauvegardée à {image_path}")
                else:
                    print(f"Ligne {index}: Colonne 'image' ne contient pas de dict")

            # Ajouter les données restantes, y compris le chemin de l'image, à la liste
            row_data = row.drop("image") if "image" in row else row
            row_data["image_path"] = image_path
            processed_data.append(row_data)

        # Sauvegarder les données restantes dans un fichier CSV
        csv_file_path = os.path.join(csv_output_dir, os.path.basename(parquet_file).replace(".parquet", ".csv"))
        pd.DataFrame(processed_data).to_csv(csv_file_path, index=False)
        print(f"Données restantes sauvegardées dans {csv_file_path}")

    except Exception as e:
        print(f"Erreur lors du traitement du fichier {parquet_file}: {e}")

# Fonction pour supprimer un fichier après traitement
def delete_parquet_file(parquet_file):
    try:
        os.remove(parquet_file)
        print(f"Fichier Parquet supprimé : {parquet_file}")
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier {parquet_file} : {e}")

# Fonction principale
def main():
    try:
        # Téléchargement des fichiers Parquet
        local_files = download_parquet_files()

        # Chemins de sortie pour les images et les CSV
        csv_output_dir = os.path.join("parquet_file_tocsv", "csv")
        image_output_dir = os.path.join("parquet_file_tocsv", "images")
        os.makedirs(csv_output_dir, exist_ok=True)
        os.makedirs(image_output_dir, exist_ok=True)

        # Traiter tous les fichiers Parquet téléchargés
        for parquet_file in local_files:
            print(f"Traitement du fichier : {parquet_file}")
            process_parquet_file(parquet_file, csv_output_dir, image_output_dir)

            # Supprimer le fichier Parquet après traitement
            delete_parquet_file(parquet_file)

        print("Traitement terminé pour tous les fichiers.")

    except Exception as e:
        print(f"Erreur dans la fonction principale : {e}")

if __name__ == "__main__":
    main()
