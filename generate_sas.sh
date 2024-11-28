#!/bin/bash

# Définir des variables
SCRIPT_DIR=$(dirname "$0")  # Répertoire du script
ENV_FILE="$SCRIPT_DIR/.env"  # Chemin vers le fichier .env

# Charger les variables depuis le fichier .env
STORAGE_ACCOUNT_NAME=$(grep -oP '^STORAGE_ACCOUNT_NAME="\K[^"]+' "$ENV_FILE")
CONTAINER_NAME=$(grep -oP '^CONTAINER_NAME="\K[^"]+' "$ENV_FILE")
STORAGE_ACCOUNT_KEY=$(grep -oP '^STORAGE_ACCOUNT_KEY="\K[^"]+' "$ENV_FILE")

# Vérifications
if [ -z "$STORAGE_ACCOUNT_NAME" ] || [ -z "$CONTAINER_NAME" ] || [ -z "$STORAGE_ACCOUNT_KEY" ]; then
    echo "Erreur : Certaines variables Azure sont absentes dans le fichier .env."
    exit 1
fi

# Définir les dates
START_TIME=$(date -u -d "-15 minutes" '+%Y-%m-%dT%H:%MZ')  # 15 minutes dans le passé
EXPIRY=$(date -u -d "+1 day" '+%Y-%m-%dT%H:%MZ')           # Expiration dans 24 heures

echo "Start Time: $START_TIME"
echo "Expiry Time: $EXPIRY"

# Générer un SAS token avec Azure CLI
SAS_TOKEN=$(az storage container generate-sas \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --name "$CONTAINER_NAME" \
    --permissions "rl" \
    --start "$START_TIME" \
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

echo "SAS Token généré avec succès et ajouté au fichier .env."
cat "$ENV_FILE"
