#!/bin/bash

# Définir des variables
SCRIPT_DIR=$(dirname "$0")  # Répertoire du script
ENV_FILE="$SCRIPT_DIR/.env"  # Chemin vers le fichier .env

# Variables Azure
STORAGE_ACCOUNT_NAME="datalakedeviavals"        # Remplacez par le nom de votre compte de stockage
CONTAINER_NAME="data"                       # Remplacez par le nom de votre conteneur
STORAGE_ACCOUNT_KEY=$(grep -oP '^STORAGE_ACCOUNT_KEY="\K[^"]+' "$ENV_FILE")  # Récupérer la clé de stockage du .env
PERMISSIONS="rl"                            # Permissions : r = lecture, l = liste
EXPIRY=$(date -u -d "1 hour" '+%Y-%m-%dT%H:%MZ') # Expiration du SAS (ici, dans 1 heure)

# Vérifier si la clé de stockage a été trouvée
if [ -z "$STORAGE_ACCOUNT_KEY" ]; then
    echo "Erreur : La clé de stockage (STORAGE_ACCOUNT_KEY) est absente dans le fichier .env."
    exit 1
fi

# Générer un SAS token avec Azure CLI
echo "Génération du SAS token..."
SAS_TOKEN=$(az storage container generate-sas \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --name "$CONTAINER_NAME" \
    --permissions "$PERMISSIONS" \
    --expiry "$EXPIRY" \
    --account-key "$STORAGE_ACCOUNT_KEY" \
    --output tsv)

if [ -z "$SAS_TOKEN" ]; then
    echo "Erreur : Impossible de générer le SAS token."
    exit 1
fi

# Ajouter ou mettre à jour le SAS_TOKEN dans le .env
if grep -q '^SAS_TOKEN=' "$ENV_FILE"; then
    sed -i "s|^SAS_TOKEN=.*|SAS_TOKEN=\"$SAS_TOKEN\"|" "$ENV_FILE"
else
    echo -e "\nSAS_TOKEN=\"$SAS_TOKEN\"" >> "$ENV_FILE"
fi

echo "Token SAS ajouté au fichier .env avec succès."
echo "Fichier .env mis à jour :"
cat "$ENV_FILE"

