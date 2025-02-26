import os
import time
import logging
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MoroccoWeatherScraper:
    def __init__(self, output_file="morocco_weather_events_VF1.csv"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Mode sans interface
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.events = []
        self.output_file = output_file

    def setup_form(self, start_date, end_date):
        """Configure le formulaire et lance la recherche."""
        try:
            self.driver.get("https://eswd.eu/cgi-bin/eswd.cgi")
            logging.info("🌍 Page chargée")

            time.sleep(3)  # Attendre le chargement de la page

            # Activer la sélection par période
            period_checkbox = self.wait.until(EC.presence_of_element_located((By.NAME, "date_selected")))
            if not period_checkbox.is_selected():
                period_checkbox.click()
            logging.info("✅ Période activée")

            # Remplir les dates
            self._set_date_field("start_date", start_date)
            self._set_date_field("end_date", end_date)

            # Sélectionner les heures
            self._set_hour_field("query_start_hour", "00")
            self._set_hour_field("query_end_hour", "24")

            logging.info(f"📅 Recherche pour {start_date} → {end_date}")

            # Sélectionner le Maroc
            country_select = Select(self.wait.until(EC.presence_of_element_located((By.NAME, "selected_countries"))))
            country_select.select_by_value("MA")
            logging.info("✅ Pays sélectionné : Maroc")

            # Soumettre
            submit_button = self.wait.until(EC.element_to_be_clickable((By.NAME, "BUT_adv_query")))
            submit_button.click()
            logging.info("📤 Formulaire soumis")

            time.sleep(5)  # Attente des résultats
            return True

        except Exception as e:
            logging.error(f"❌ Erreur formulaire : {str(e)}")
            return False

    def _set_date_field(self, field_name, date_value):
        """Définit une date dans un champ input."""
        field = self.wait.until(EC.presence_of_element_located((By.ID, field_name)))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", field)
        field.clear()
        field.send_keys(date_value)

    def _set_hour_field(self, field_name, hour_value):
        """Définit une heure dans un champ select."""
        hour_select = Select(self.driver.find_element(By.NAME, field_name))
        hour_select.select_by_value(hour_value)

    def parse_events(self):
        """Récupère les événements de la page."""
        try:
            time.sleep(5)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Vérifier s'il n'y a pas d'événements
            if soup.find("p", string=lambda text: text and "number of selected reports: 0" in text):
                logging.warning("⚠ Aucun événement trouvé pour cette période.")
                return

            entries = soup.find_all("tr", id=lambda x: x and x.startswith("MA_"))
            if not entries:
                logging.warning("⚠ Aucun événement récupéré.")
                return

            for entry in entries:
                try:
                    # ✅ Extraction du type d'événement
                    event_type = "N/A"
                    event_type_tag = entry.find("td")
                    if event_type_tag:
                        event_bold = event_type_tag.find("p")
                        if event_bold and event_bold.b:
                            event_type = event_bold.b.get_text(strip=True)

                    if event_type == "N/A":
                        logging.warning(f"⚠ Type d'événement introuvable pour : {entry}")

                    # ✅ Extraction des informations principales
                    base_info = entry.find("td", class_="base_info")
                    details_info = entry.find("td", class_="detail_info")

                    if not base_info or not details_info:
                        logging.warning("⚠ Infos manquantes, événement ignoré.")
                        continue

                    location, region, country, latitude, longitude, date_event, time_event = "N/A", "N/A", "Morocco", "N/A", "N/A", "N/A", "N/A"

                    # ✅ Analyse du texte de la section "base_info"
                    raw_text = base_info.get_text("\n", strip=True).split("\n")
                    for part in raw_text:
                        part = part.strip()
                        if "Morocco" in part:
                            country = "Morocco"
                        elif "-" in part and len(part) == 10:
                            date_event = part
                        elif ":" in part:
                            time_event = part
                        elif "(" in part and ")" in part:  # ✅ Extraction des coordonnées GPS
                            coords_match = re.search(r"\(([\d\.]+)\s*N,\s*([\d\.]+)\s*W\)", part)
                            if coords_match:
                                latitude, longitude = coords_match.groups()
                        elif " | " in part:
                            region, location = part.split(" | ")
                        elif region == "N/A":
                            region = part
                        elif location == "N/A":
                            location = part

                    # ✅ Extraction des détails
                    details = details_info.get_text(" ", strip=True) if details_info else "N/A"

                    # ✅ Extraction du nombre de morts (via regex)
                    deaths = "0"
                    match = re.search(r"Number of people dead: (\d+)", details)
                    if match:
                        deaths = match.group(1)

                    # ✅ Correction des valeurs manquantes
                    if location == "N/A" and region != "N/A":
                        location = region  

                    # ✅ Ajouter l'événement (SUPPRESSION DE "Report Status")
                    self.events.append([event_type, location, region, country, latitude, longitude, date_event, time_event, details, deaths, "#map_div"])

                except Exception as e:
                    logging.warning(f"⚠ Erreur parsing événement : {str(e)}")

        except Exception as e:
            logging.error(f"❌ Erreur parsing : {str(e)}")

    def scrape_data(self, start_year=2000, end_year=2024):
        """Scrape les données mois par mois de 2000 à 2024."""
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                start_date = f"01-{month:02d}-{year}"
                end_date = (datetime.strptime(start_date, "%d-%m-%Y") + timedelta(days=30)).strftime("%d-%m-%Y")

                logging.info(f"📅 Récupération {start_date} → {end_date}")
                if self.setup_form(start_date, end_date):
                    self.parse_events()
                time.sleep(3)

    def save_to_csv(self):
        """Sauvegarde les événements dans un fichier CSV (SANS "Report Status")."""
        df = pd.DataFrame(self.events, columns=["Event Type", "Location", "Region", "Country", "Latitude", "Longitude", "Date", "Time UTC", "Details", "Deaths", "Source Link"])
        df.to_csv(self.output_file, index=False, encoding="utf-8")
        logging.info(f"✅ Données sauvegardées : {self.output_file}")

    def close(self):
        """Ferme le navigateur."""
        self.driver.quit()
        logging.info("🔴 Navigateur fermé")

# ------------------------
# 🚀 Exécution
# ------------------------
if __name__ == "__main__":
    scraper = MoroccoWeatherScraper()
    try:
        scraper.scrape_data(2000, 2024)
        scraper.save_to_csv()
    finally:
        scraper.close()
