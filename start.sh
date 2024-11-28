#!/bin/bash

# Activer le mode strict pour arrêter le script en cas d'erreur
set -e

# Afficher chaque commande exécutée (optionnel pour le débogage)
set -x

# Chemin vers les scripts
SCRIPT_DIR=$(dirname "$0")

# 0. Activer l'environnement virtuel et installer les dépendances
echo "Étape 0 : Activation de l'environnement virtuel et installation des dépendances..."

# Créer l'environnement virtuel si nécessaire
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
fi

# Activer l'environnement virtuel
source "$VENV_DIR/bin/activate"

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r "$SCRIPT_DIR/requirements.txt"

# 1. Lancer le script pour installer ODBC
echo "Étape 1 : Installation de ODBC..."
bash "$SCRIPT_DIR/install_odbc_18.sh"

# 1. Lancer le script pour se connecter à Azure
echo "Étape 2 : Connexion à Azure..."
bash "$SCRIPT_DIR/az_login.sh"

# 2. Lancer le script pour générer un SAS token
echo "Étape 3 : Génération du SAS token..."
bash "$SCRIPT_DIR/generate_sas.sh"

# 3. Exécuter le script Python pour traiter les fichiers CSV
echo "Étape 4 : Traitement des fichiers CSV..."
python3 "$SCRIPT_DIR/script_azuresql.py"

# 3. Exécuter le script Python pour traiter les fichiers Parquet
echo "Étape 5 : Traitement des fichiers Parquet..."
python3 "$SCRIPT_DIR/script_parquet.py"

# 4. Exécuter le script Python pour traiter le fichier ZIP (reviews.zip)
echo "Étape 6 : Traitement du fichier ZIP..."
python3 "$SCRIPT_DIR/script_zip.py"

# 5. Exécuter le script Python pour traiter les autres fichiers dans 'nlp_data'
echo "Étape 7 : Traitement des autres fichiers NLP..."
python3 "$SCRIPT_DIR/script_nlpdata.py"

echo "Tous les scripts ont été exécutés avec succès."

# Désactiver l'environnement virtuel
deactivate