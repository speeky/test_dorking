from seleniumbase import SB
import random
import time
import os

# Paramètres (à ajuster selon ton besoin)
dork = os.getenv("QUERY", 'intext:"SQL syntax near" | intext:"syntax error has occurred"')
domain = "example.com"  # Remplace par ton domaine cible
query = f"{dork} site:{domain}"

def main():
    with SB(uc=True, headless=False, slow_mo=0.5) as sb:  # UC Mode + visible pour debug, léger ralentissement
        # Activation de CDP Mode pour furtivité
        sb.activate_cdp_mode("https://www.google.com")
        sb.sleep(random.uniform(5, 8))  # Temps pour chargement initial

        # Gestion de la fenêtre de cookies/consentement
        try:
            sb.wait_for_element_visible("#L2AGLb", timeout=10)
            sb.click("#L2AGLb")
            sb.sleep(random.uniform(1, 3))
            print("Cookies acceptés.")
        except Exception as e:
            print(f"Échec gestion cookies : {e}")

        # Détection initiale de CAPTCHA ou blocage
        if "sorry" in sb.get_current_url() or sb.is_element_visible("iframe[src*='recaptcha']", timeout=5):
            print("CAPTCHA ou blocage détecté au chargement.")
            sb.uc_gui_click_captcha()
            sb.sleep(5)
            if "sorry" in sb.get_current_url():
                sb.screenshot("captcha_initial.png")
                raise Exception("CAPTCHA persistant. Change d'IP ou attends.")

        # Simulation de comportement humain
        sb.execute_script(f"window.scrollBy(0, {random.randint(200, 600)})")
        sb.sleep(random.uniform(1, 2))
        sb.move_to_element("body", 300, 300)  # Mouvement de souris
        sb.sleep(random.uniform(0.5, 1))

        # Recherche avec sélecteurs alternatifs
        search_selectors = ['input[name="q"]', '#APjFqb']  # #APjFqb est un ID alternatif
        search_box = None
        for selector in search_selectors:
            try:
                sb.wait_for_element_visible(selector, timeout=15)
                search_box = selector
                sb.click(selector)
                break
            except Exception:
                continue
        if not search_box:
            sb.screenshot("error_searchbox.png")
            raise Exception("Barre de recherche non trouvée après 15 secondes.")

        # Saisie lente du dork
        for char in query:
            sb.type(search_box, char)
            sb.sleep(random.uniform(0.05, 0.15))
        sb.sleep(random.uniform(0.5, 1))
        sb.enter()
        sb.sleep(random.uniform(4, 6))

        # Détection de CAPTCHA après recherche
        if "sorry" in sb.get_current_url() or sb.is_element_visible("iframe[src*='recaptcha']", timeout=5):
            print("CAPTCHA détecté après recherche.")
            sb.uc_gui_click_captcha()
            sb.sleep(5)
            if "sorry" in sb.get_current_url():
                sb.screenshot("captcha_post_search.png")
                raise Exception("CAPTCHA persistant après recherche.")

        # Extraction des résultats
        titles = sb.get_text_list("h3")  # Titres des résultats
        if titles:
            print("Résultats trouvés :")
            with open("results.txt", "w", encoding="utf-8") as f:
                for title in titles:
                    print(title)
                    f.write(title + "\n")
        else:
            print("Aucun résultat trouvé.")
            sb.screenshot("no_results.png")

        # Capture d'écran finale
        sb.screenshot("results.png")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erreur principale : {e}")
        if 'sb' in locals():
            sb.screenshot("error.png")
