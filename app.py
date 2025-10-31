import streamlit as st
import pandas as pd
from hellowork import scrape_hellowork_playwright
from indeed import scrape_indeed
from france_travail import scrape_francetravail
import random
import time

# -----------------------------
# Configuration Streamlit
# -----------------------------
st.set_page_config(page_title="Scrappeur d'offres", page_icon="💼", layout="centered")

st.title("💼 Scrappeur d'offres d'emploi multi-sites")
st.markdown("""
Ce scrappeur recherche automatiquement des offres d’emploi sur plusieurs sites :  
**HelloWork**, **Indeed**, **France Travail** *(et bientôt WelcomeToTheJungle, Jobteaser...)*.
""")

# -----------------------------
# Entrées utilisateur
# -----------------------------
keyword = st.text_input("🔍 Mot-clé", "Web developer")
location = st.text_input("📍 Ville", "Toulouse")
pages = st.slider("📄 Nombre de pages à parcourir", 1, 10, 3)
filtre_alternance = st.checkbox("📌 Filtrer uniquement Alternance (HelloWork uniquement)", value=True)

# Choix des sites à scraper
sites = st.multiselect(
    "🌐 Choisir les sites à scraper :",
    ["HelloWork", "Indeed", "France Travail"],
    default=["HelloWork", "Indeed", "France Travail"]
)

# -----------------------------
# Lancement du scraping
# -----------------------------
if st.button("🚀 Lancer le scraping"):
    with st.spinner("Scraping en cours..."):
        dfs = []

        # --- HelloWork ---
        if "HelloWork" in sites:
            st.info("🔎 Scraping HelloWork en cours...")
            try:
                df_hellowork = scrape_hellowork_playwright(keyword, location, pages, filtre_alternance)
                if not df_hellowork.empty:
                    dfs.append(df_hellowork)
                    st.success(f"✅ {len(df_hellowork)} offres récupérées depuis HelloWork")
                else:
                    st.warning("Aucune offre trouvée sur HelloWork.")
            except Exception as e:
                st.error(f"Erreur sur HelloWork : {e}")
            time.sleep(random.uniform(1, 2))

        # --- Indeed ---
        if "Indeed" in sites:
            st.info("🔎 Scraping Indeed en cours...")
            try:
                df_indeed = scrape_indeed(keyword, location, pages)
                if not df_indeed.empty:
                    dfs.append(df_indeed)
                    st.success(f"✅ {len(df_indeed)} offres récupérées depuis Indeed")
                else:
                    st.warning("Aucune offre trouvée sur Indeed.")
            except Exception as e:
                st.error(f"Erreur sur Indeed : {e}")
            time.sleep(random.uniform(1, 2))

        # --- France Travail ---
        if "France Travail" in sites:
            st.info("🔎 Scraping France Travail en cours...")
            try:
                df_france = scrape_francetravail(keyword, "31555", pages=pages)
                if not df_france.empty:
                    dfs.append(df_france)
                    st.success(f"✅ {len(df_france)} offres récupérées depuis France Travail")
                else:
                    st.warning("Aucune offre trouvée sur France Travail.")
            except Exception as e:
                st.error(f"Erreur sur France Travail : {e}")
            time.sleep(random.uniform(1, 2))

        # -----------------------------
        # Fusion et nettoyage des résultats
        # -----------------------------
        if dfs:
            # ✅ Harmoniser les colonnes avant la fusion
            for df in dfs:
                if "Entreprise" not in df.columns:
                    df["Entreprise"] = ""

            df_total = pd.concat(dfs, ignore_index=True)
            df_total.drop_duplicates(subset=["Titre", "Entreprise"], inplace=True)

            st.success(f"🎉 Total : {len(df_total)} offres trouvées sur {', '.join(sites)}")
            st.dataframe(df_total)

            # Graphique de répartition
            st.subheader("📊 Répartition par site")
            st.bar_chart(df_total["Site"].value_counts())

            # Téléchargement CSV
            csv = df_total.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="💾 Télécharger le CSV",
                data=csv,
                file_name=f"offres_{keyword}_{location}.csv",
                mime="text/csv",
            )
        else:
            st.warning("❌ Aucune offre trouvée sur les sites sélectionnés.")


