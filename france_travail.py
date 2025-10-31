from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random


def scrape_francetravail(keyword, location_code="31555", rayon=10, pages=2):
    """
    Scrape les offres sur France Travail (ex: Pôle Emploi)
    Args:
        keyword (str): Mot-clé de recherche
        location_code (str): Code commune (ex: 31555 = Toulouse)
        rayon (int): Rayon de recherche en km
        pages (int): Nombre de pages à parcourir
    """
    base_url = "https://candidat.francetravail.fr/offres/recherche"
    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_num in range(1, pages + 1):
            url = (
                f"{base_url}?lieux={location_code}"
                f"&motsCles={keyword.replace(' ', '+')}"
                f"&offresPartenaires=true&rayon={rayon}&tri=0&page={page_num}"
            )
            print(f"[France Travail] Scraping page {page_num} → {url}")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("li.result", timeout=15000)
                time.sleep(random.uniform(2, 3))

                cards = page.query_selector_all("li.result")
                if not cards:
                    print("⚠️ Aucune offre trouvée sur cette page.")
                    continue

                for card in cards:
                    try:
                        h2_elem = card.query_selector("h2.media-heading")
                        titre_elem = card.query_selector("span.media-heading-title")
                        subtext_elem = card.query_selector("p.subtext")
                        desc_elem = card.query_selector("p.description")
                        contrat_elem = card.query_selector("p.contrat")

                        # 🔹 Récupération du titre
                        titre = titre_elem.inner_text().strip() if titre_elem else ""

                        # 🔹 Récupération du lien à partir de l’ID
                        offre_id = h2_elem.get_attribute("data-intitule-offre") if h2_elem else None
                        lien = (
                            f"https://candidat.francetravail.fr/offres/recherche/detail/{offre_id}"
                            if offre_id
                            else ""
                        )

                        # 🔹 Description et contrat
                        description = desc_elem.inner_text().strip() if desc_elem else ""
                        contrat = contrat_elem.inner_text().strip() if contrat_elem else ""

                        # 🔹 Extraction entreprise + lieu
                        entreprise, lieu = "", ""
                        if subtext_elem:
                            subtext_text = subtext_elem.inner_text().strip()
                            if " - " in subtext_text:
                                parts = subtext_text.split(" - ", 1)
                                entreprise = parts[0].strip()
                                lieu = parts[1].strip()
                            else:
                                lieu = subtext_text.strip()

                        if titre:
                            all_jobs.append({
                                "Site": "France Travail",
                                "Titre": titre,
                                "Entreprise": entreprise,
                                "Lieu": lieu,
                                "Contrat": contrat,
                                "Description": description,
                                "Lien": lien
                            })
                    except Exception as e:
                        print(f"⚠️ Erreur parsing offre : {e}")
                        continue

                print(f"✅ Page {page_num} : {len(all_jobs)} offres cumulées")
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"⚠️ Erreur page {page_num} : {e}")

        browser.close()

    df = pd.DataFrame(all_jobs)
    df.drop_duplicates(subset=["Titre", "Entreprise"], inplace=True)
    return df
