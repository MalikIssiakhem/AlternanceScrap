from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random


def scrape_indeed(keyword, location, pages=2, headless=False):
    """
    Scrape les offres Indeed (version 2025).
    Contourne le blocage headless et simule un comportement humain.
    """
    jobs = []
    base_url = "https://fr.indeed.com/jobs"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        for page_num in range(pages):
            start = page_num * 10
            url = f"{base_url}?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}&radius=25&start={start}"
            print(f"[Indeed] Scraping page {page_num + 1} → {url}")

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(random.uniform(3, 5))

                # Scroll progressif pour forcer le rendu des offres
                for _ in range(5):
                    page.mouse.wheel(0, random.randint(500, 1200))
                    time.sleep(random.uniform(0.8, 1.5))

                # Attente dynamique des offres
                cards = page.query_selector_all("div.job_seen_beacon")
                if not cards:
                    print("⚠️ Aucun job trouvé sur cette page (possiblement page vide / anti-bot)")
                    continue

                for card in cards:
                    try:
                        titre_elem = card.query_selector("h2.jobTitle span")
                        entreprise_elem = card.query_selector("span[data-testid='company-name']")
                        lieu_elem = card.query_selector("div[data-testid='text-location']")
                        contrat_elem = card.query_selector("div.metadata, div.jobMetadataHeader")
                        lien_elem = card.query_selector("h2.jobTitle a")

                        titre = titre_elem.inner_text().strip() if titre_elem else ""
                        entreprise = entreprise_elem.inner_text().strip() if entreprise_elem else ""
                        lieu = lieu_elem.inner_text().strip() if lieu_elem else ""
                        contrat = contrat_elem.inner_text().strip() if contrat_elem else ""
                        lien = (
                            "https://fr.indeed.com" + lien_elem.get_attribute("href")
                            if lien_elem and lien_elem.get_attribute("href")
                            else ""
                        )

                        if titre:
                            jobs.append({
                                "Site": "Indeed",
                                "Titre": titre,
                                "Entreprise": entreprise,
                                "Lieu": lieu,
                                "Contrat": contrat,
                                "Lien": lien,
                            })
                    except Exception:
                        continue

                print(f"✅ Page {page_num + 1} : {len(cards)} offres détectées")
                time.sleep(random.uniform(3, 6))

            except Exception as e:
                print(f"⚠️ Erreur page {page_num + 1} : {e}")

        browser.close()

    df = pd.DataFrame(jobs)
    df.drop_duplicates(subset=["Titre", "Entreprise"], inplace=True)
    return df
