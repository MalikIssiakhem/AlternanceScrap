from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_hellowork_playwright(keyword, location, pages=3, filtre_alternance=True):
    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for page_num in range(1, pages + 1):
            url = f"https://www.hellowork.com/fr-fr/emploi/recherche.html?k={keyword}&l={location}&p={page_num}"
            page.goto(url)
            page.wait_for_selector("div[data-cy='serpCard']", timeout=15000)
            time.sleep(2)

            cards = page.query_selector_all("div[data-cy='serpCard']")
            for card in cards:
                try:
                    titre_elem = card.query_selector("a[data-cy='offerTitle'] h3 p:first-child")
                    entreprise_elem = card.query_selector("a[data-cy='offerTitle'] h3 p:nth-child(2)")
                    lieu_elem = card.query_selector("div[data-cy='localisationCard']")
                    contrat_elem = card.query_selector("div[data-cy='contractCard']")
                    lien_elem = card.query_selector("a[data-cy='offerTitle']")

                    titre = titre_elem.inner_text().strip() if titre_elem else ""
                    entreprise = entreprise_elem.inner_text().strip() if entreprise_elem else ""
                    lieu = lieu_elem.inner_text().strip() if lieu_elem else ""
                    contrat = contrat_elem.inner_text().strip() if contrat_elem else ""
                    lien = "https://www.hellowork.com" + lien_elem.get_attribute("href") if lien_elem else ""

                    if filtre_alternance and "Alternance" not in contrat:
                        continue

                    all_jobs.append({
                        "Site": "HelloWork",
                        "Titre": titre,
                        "Entreprise": entreprise,
                        "Lieu": lieu,
                        "Contrat": contrat,
                        "Lien": lien
                    })
                except Exception:
                    continue

            time.sleep(1)

        browser.close()

    df = pd.DataFrame(all_jobs)
    df.drop_duplicates(subset=["Titre", "Entreprise"], inplace=True)
    return df
