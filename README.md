# MoroccoWeatherScraper
Script Python pour scraper les événements météorologiques au Maroc

Ce scraper en Python collecte des événements météorologiques extrêmes au Maroc depuis le site ESWD et stocke les résultats dans un fichier CSV.

🌍 Fonctionnalités

✔️ Scrape les événements météorologiques de 2000 à 2024 (mois par mois)
✔️ Collecte des informations détaillées :

Type d'événement
Lieu (ville, région, pays)
Coordonnées GPS (latitude & longitude)
Date et heure de l'événement
Détails sur les dommages et les victimes
✔️ Enregistre les résultats dans un fichier CSV

🛠️ Configuration et Installation

1️⃣ Cloner le dépôt GitHub
Dans un terminal, exécutez :

git clone https://github.com/Diane-Fadwa/MoroccoWeatherScraper.git
cd MoroccoWeatherScraper

2️⃣ Créer un environnement virtuel : Cela permet d'isoler les dépendances du projet.
Assurez-vous d'avoir Python 3.x installé
➤ Sur macOS/Linux

python3 -m venv venv
source venv/bin/activate

➤ Sur Windows (cmd)

python -m venv venv
venv\Scripts\activate

3️⃣ Installer les dépendances
Le script utilise plusieurs bibliothèques Python :

selenium : automatisation du navigateur

beautifulsoup4 : parsing HTML

pandas : manipulation de données

chromedriver-autoinstaller : gestion du driverChrome

Installez-les avec :
pip install -r requirement.txt

🚀 Utilisation du Scraper

Lancez le script Python pour commencer le scraping des données :
python3 eswd1.py

Le fichier CSV généré (morocco_weather_events_VF1.csv) sera enregistré dans le dossier du projet.

🔧 Personnalisation : Modifier la période

Par défaut, le script collecte les données de 2000 à 2024.
Vous pouvez changer ces valeurs dans :

scraper.scrape_data(2005, 2015) 

🛠 Dépannage

1️⃣ Erreur "chromedriver not found"
Vérifiez que ChromeDriver est bien installé et accessible :

chromedriver --version
Si l'erreur persiste, ajoutez le chemin absolu :

self.driver = webdriver.Chrome

(executable_path="CHEMIN_VERS_CHROMEDRIVER", options=chrome_options)

2️⃣ Aucune donnée récupérée

✔️ Vérifiez votre connexion Internet.

✔️ Testez manuellement l’URL dans un navigateur : https://eswd.eu/cgi-bin/eswd.cgi

✔️ Assurez-vous que le site n'a pas changé sa structure HTML.
