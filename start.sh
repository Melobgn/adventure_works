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

# Pause pour permettre l'installation de se terminer correctement
sleep 2

# 1. Lancer le script pour installer ODBC
echo "Étape 1 : Installation de ODBC..."
bash "$SCRIPT_DIR/install_odbc_18.sh"

# Pause pour permettre à l'installation de se finaliser
sleep 2

# 1. Lancer le script pour se connecter à Azure
echo "Étape 2 : Connexion à Azure..."
bash "$SCRIPT_DIR/az_login.sh"

# Pause pour stabiliser la connexion Azure
sleep 2

# 2. Lancer le script pour générer un SAS token
echo "Étape 3 : Génération du SAS token..."
bash "$SCRIPT_DIR/generate_sas.sh"

# Pause pour permettre au SAS token d'être correctement généré et mis à jour
sleep 2

# 3. Exécuter le script Python pour traiter les fichiers CSV

echo "Étape 4 : Traitement des fichiers CSV..."
python3 "$SCRIPT_DIR/script_azuresql.py"

# Pause pour éviter des conflits dans les accès aux ressources
sleep 2

# 3. Exécuter le script Python pour traiter les fichiers Parquet
echo "Étape 5 : Traitement des fichiers Parquet..."
python3 "$SCRIPT_DIR/script_parquet.py"

# Pause pour permettre à l'étape précédente de se stabiliser
sleep 2

# 4. Exécuter le script Python pour traiter le fichier ZIP (reviews.zip)
echo "Étape 6 : Traitement du fichier ZIP..."
python3 "$SCRIPT_DIR/script_zip.py"

# Pause pour permettre la gestion des fichiers extraits
sleep 2

# 5. Exécuter le script Python pour traiter les autres fichiers dans 'nlp_data'
echo "Étape 7 : Traitement des autres fichiers NLP..."
python3 "$SCRIPT_DIR/script_nlpdata.py"

# Désactiver l'environnement virtuel
deactivate

echo "Tous les scripts ont été exécutés avec succès."
