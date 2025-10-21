#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import sys

# Paramètres via variables d'environnement
dork = os.getenv("QUERY", 'intext:"SQL syntax near" | intext:"syntax error has occurred"')
domain = os.getenv("TARGET_DOMAIN", "example.com")
query = f"{dork} site:{domain}"

def main():
    driver = None
    try:
        # Configuration du pilote Chrome (automatique via webdriver_manager)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        # Ouvre Google
        driver.get("https://www.google.com/ncr")  # /ncr évite la redirection locale
        
        # Gestion des cookies
        try:
            cookie_button = driver.find_element(By.ID, "L2AGLb")
            cookie_button.click()
            print("Cookies acceptés.")
            time.sleep(2)  # Attend que la page se recharge
        except Exception:
            print("Aucun bouton de cookies trouvé ou clic échoué, continuation...")
        
        # Recherche
        try:
            search_box = driver.find_element(By.NAME, "q")  # Barre de recherche
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)  # Attente pour charger les résultats
            
            # Détection de CAPTCHA
            if "sorry" in driver.current_url:
                print("CAPTCHA détecté — arrêt.")
                driver.save_screenshot("captcha_detected.png")
                return
            
            # Extraction des titres
            titles = driver.find_elements(By.TAG_NAME, "h3")
            if titles:
                print(f"Résultats trouvés ({len(titles)})")
                with open("results.txt", "w", encoding="utf-8") as f:
                    for title in titles:
                        print(title.text)
                        f.write(title.text + "\n")
            else:
                print("Aucun résultat trouvé.")
                driver.save_screenshot("no_results.png")
        except Exception as e:
            print(f"Erreur lors de la recherche : {e}")
            driver.save_screenshot("error_search.png")
            raise
        
        # Capture finale
        driver.save_screenshot("results.png")
    
    except Exception as exc:
        print(f"Erreur principale : {exc}", file=sys.stderr)
        try:
            if driver:
                driver.save_screenshot("error.png")
        except Exception:
            pass
        raise
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Sécurité : éviter Google directement
    if domain in ("google.com", "www.google.com"):
        print("Interdit : ne pas automatiser Google directement. Utilise l'API Custom Search.")
        sys.exit(1)
    try:
        main()
    except Exception:
        pass
