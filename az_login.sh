#!/bin/bash

# Chemin vers le fichier .env contenant les variables
ENV_FILE=".env"

# Vérifier si Azure CLI est installé
if ! command -v az &>/dev/null; then
    echo "Azure CLI n'est pas installé. Veuillez l'installer avant d'exécuter ce script."
    exit 1
fi

# Charger les variables d'environnement depuis .env
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Le fichier .env est manquant. Veuillez le créer avec les variables d'environnement nécessaires."
    exit 1
fi

# Vérifier si SUBSCRIPTION_ID est défini
if [ -z "$SUBSCRIPTION_ID" ]; then
    echo "Erreur : SUBSCRIPTION_ID n'est pas défini dans le fichier .env."
    exit 1
fi

# Se connecter à Azure (interactif)
echo "Connexion à Azure..."
az login --use-device-code
if [ $? -ne 0 ]; then
    echo "Échec de la connexion à Azure. Veuillez vérifier vos identifiants."
    exit 1
fi

# Définir l'abonnement
echo "Définition de l'abonnement : $SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"
if [ $? -ne 0 ]; then
    echo "Erreur lors de la définition de l'abonnement. Vérifiez l'ID de l'abonnement."
    exit 1
fi

# Afficher un message pour confirmer la connexion
echo "Connexion réussie à Azure avec l'abonnement : $SUBSCRIPTION_ID"

# Exécuter d'autres scripts ou commandes après la connexion
# Remplacez ci-dessous par les scripts Python ou Bash que vous voulez lancer
# echo "Lancement des scripts supplémentaires..."
# python3 script_parquet_processing.py
# python3 another_script.py
# ./other_bash_script.sh

# echo "Tous les scripts ont été exécutés."
