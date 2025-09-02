from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json



def fill_fields(data: dict):
    """
    Ouvre le navigateur, navigue vers l'URL cible et remplit les champs
    d'après les clés du dictionnaire `data`.
    Clés attendues dans `data` :
      - "code_profil"
      - "fonction"
      - "type"
      - "par"
      - "acces"
      - "options_exist"
      - "options_restric"
    """

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            print("[ERREUR] Le contenu reçu n’est pas un JSON valide.")
            return


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://192.168.1.33:8124/auth/login/page")

    driver.maximize_window()

    print("Page title is:", driver.title)
    options = Options()



    login_input = driver.find_element(By.ID, "login")
    login_input.send_keys("STAGEIA")  

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys("Azerty.01")  

    submit_button = driver.find_element(By.ID, "go-basic")
    submit_button.click()


    wait = WebDriverWait(driver, 20)

    # 1. Ouvrir menu
    try:
        print("[INFO] Attente du menu principal (menu1)...")
        menu1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s_profile_bar_iconlink[aria-label='Ouvrir le menu de navigation']")))
        print("[INFO] menu1 trouvé, clic...")
        menu1.click()
        print("[INFO] menu1 cliqué. Attente du menu flottant...")
        # Attendre que le menu flottant soit visible
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='sitemap-page']")))
        print("[INFO] Menu flottant visible.")
    except Exception as e:
        print(f"[ERREUR] Impossible de cliquer sur menu1 ou d'afficher le menu flottant : {e}")
        driver.quit()
        exit(1)


    time.sleep(0.5)



    try:
        menu2 = driver.find_element(By.ID, "b953fbe4-b704-414c-9f7e-493545d0898a")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu2)
        time.sleep(0.5)
        menu2.click()
        print("[INFO] menu2 cliqué.")
    except Exception as e:
        print(f"[ERREUR] Impossible de cliquer sur menu2 : {e}")
        driver.quit()
        exit(1)





    try:
        print("[INFO] Attente du troisième menu (menu3)...")
        menu3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='s_app_body']/div/article/div[2]/header/div[1]/div/div[4]/div/div[1]/div[1]/a/div")))
        print("[INFO] menu3 trouvé, clic...")
        menu3.click()
        print("[INFO] menu3 cliqué.")
    except Exception as e:
        print(f"[ERREUR] Impossible de cliquer sur menu3 : {e}")
        driver.quit()
        exit(1)
    time.sleep(5)

    # ---------------------------------------choix du profil--------------------------------------------------------



    if data.get("code_profil"):
        input_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[contains(@class, "s-inplace-input") and contains(@class, "s-filter-criteria-cell-input") and @maxlength="5"]')))
        input_field.send_keys(data["code_profil"])

        time.sleep(5)

    if data.get("fonction"):
        input_field = wait.until(EC.presence_of_element_located((By.XPATH, '//input[contains(@class, "s-inplace-input") and contains(@class, "s-filter-criteria-cell-input") and @maxlength="12"]')))
        input_field.send_keys(data["fonction"])
        input_field.send_keys(Keys.ENTER)
        time.sleep(2)

        table = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 's-grid-table-body')))

        # Cliquer sur la table
        table.click()

        time.sleep(3)



    # -----------------------------------------------------choix du type---------------------------------------------------------------



    if data['type']!="":


        btn = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                '//div[input[@type="text" and @maxlength="15" and contains(@class, "s-inplace-input")]]//a[@title="Liste à choix libre"]'
            )))
        btn.click()

        time.sleep(2)

        if data['type']=="Regroupement":


            regroupement_btn = wait.until(EC.element_to_be_clickable((
                            By.XPATH,
                            '//ul[contains(@class, "s-list-default-ul")]'
                            '//li[contains(@class, "s-selected")]'
                            '//a[contains(@class, "s-list-default-btn-default") and @title="Regroupement" and normalize-space(text())="Regroupement"]'
                        )))

            regroupement_btn.click()

            time.sleep(2)
        elif data['type']=="Site": 
            site_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                    '//ul[contains(@class, "s-list-default-ul")]'
                    '//li[contains(@class, "s-list-default-li")]'
                    '//a[contains(@class, "s-list-default-btn-default") and @title="Site" and normalize-space(text())="Site"]'
            )))

                        
            site_btn.click()
            time.sleep(2)
        
    






    # ---------------------------------------choix du regroupement oubien site ------------------------------------------------



    if data['type']!="":

        input_elem = driver.find_element(By.XPATH, '//div[@class="s-grid-cell-value-edit s-inplace-value-edit"][.//input[@maxlength="5"]]/a[@title="Sélection" and contains(@class,"s-btn-lookup")]')
        input_elem.click()

        time.sleep(2)

        # choix du site de la liste 

        if data.get("par"):
            cav_button = driver.find_element(
                By.XPATH,
                '//tr[contains(@class, "s-grid-row") and contains(@class, "s-record-selector-row")]'
                '//td[1]/div[normalize-space(text())="{data["par"]}"]'
            )

            cav_button.click()






    #-------------------------------------------choix d'accès-----------------------------------------------------------------
    if data['acces']!="":
        if data.get("acces"):
            liste_btn = driver.find_element(
                By.XPATH,
                '//div[@class="s-grid-cell-value-edit s-inplace-value-edit"]'
                '[.//input[@maxlength="6" and @readonly="readonly" and contains(@class, "s-inplace-input")]]'
                '//a[@title="Liste à choix libre" and contains(@class, "s-btn-expand_m")]'
            )

            liste_btn.click()    
            time.sleep(1)


            if data["acces"] == "Oui":
                Oui_btn = wait.until(EC.element_to_be_clickable((
                                By.XPATH,
                                '//ul[contains(@class, "s-list-default-ul")]'
                                '//li[contains(@class, "s-selected")]'
                                '//a[contains(@class, "s-list-default-btn-default") and @title="Oui" and normalize-space(text())="Oui"]'
                            )))

                Oui_btn.click()

                time.sleep(2)


            else:          
                Non_btn = wait.until(EC.element_to_be_clickable((
                        By.XPATH,
                            '//ul[contains(@class, "s-list-default-ul")]'
                            '//li[contains(@class, "s-list-default-li")]'
                            '//a[contains(@class, "s-list-default-btn-default") and @title="Non" and normalize-space(text())="Non"]'
                        )))

                                
                Non_btn.click()
                time.sleep(2)




    #---------------------------------------------choix des options--------------------------------------------------
    if data["options_exist"].__len__() > 0:
        
        to_delete = set(data["options_restric"])
        # 2. On filtre ch1 en excluant ceux qui sont dans to_delete
        result = "".join(c for c in data["options_exist"] if c not in to_delete)
        input_field = driver.find_element(
            By.XPATH,
                '//div[@class="s-grid-cell-value-edit s-inplace-value-edit"]'
                '[.//a[@title="Actions" and contains(@class, "s-btn-menus")]]'
                '//input[@maxlength="23" and contains(@class, "s-inplace-input")]'
            )

        # Supprimer le contenu existant si besoin, puis écrire
        input_field.clear()
        input_field.send_keys(result)





#--------------------------validation------------







    input("Test terminé. Appuyez sur Entrée pour fermer le navigateur...")









