from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


def fill_user(data: dict):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://192.168.1.33:8124/auth/login/page")

    driver.maximize_window()

    print("Page title is:", driver.title)




    login_input = driver.find_element(By.ID, "login")
    login_input.send_keys("STAGEIA")  

    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys("Azerty.01")  

    submit_button = driver.find_element(By.ID, "go-basic")
    submit_button.click()


    wait = WebDriverWait(driver, 15)

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

    try:
        menu2 = driver.find_element(By.ID, "9a0679e8-2ee3-455d-aa65-54ef6c7e8b01")
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
        menu3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='s_app_body']/div/article/div[2]/header/div[1]/div/div[4]/div/div[1]/div[1]/a")))
        print("[INFO] menu3 trouvé, clic...")
        menu3.click()
        print("[INFO] menu3 cliqué.")
    except Exception as e:
        print(f"[ERREUR] Impossible de cliquer sur menu3 : {e}")
        driver.quit()
        exit(1)

    # 4. Saisie et attente sans sleep
    Code = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.s-field-input[maxlength="5"]')))
    Code.send_keys(data["Code"])

    if data["Nom"]!="":
        Nom = driver.find_element(By.CSS_SELECTOR, 'input.s-field-input[maxlength="30"]')
        Nom.send_keys(data["Nom"])
        time.sleep(1)

    actif = driver.find_element(By.CSS_SELECTOR, 'input.s-field-checkbox.s-field-input-boolean[type="checkbox"]')
    actif.click()  


    # general 

    # Cocher la case "Connexion X3"
    if data["Connexion_X3"]==True:
        Connexion_X3 = driver.find_element(By.XPATH, '//label[contains(text(), "Connexion X3")]/following::input[@type="checkbox"]')
        Connexion_X3.click()
        time.sleep(1)

    # Cocher la case "Connexion services web"
    if data["Connexion_WS"]==True:
        Connexion_WS = driver.find_element(By.XPATH, '//label[contains(text(), "Connexion services web")]/following::input[@type="checkbox"]')
        Connexion_WS.click()
        time.sleep(1)

    # Cocher la case "Demandeur"
    if data["Demandeur"]==True:
        Demandeur = driver.find_element(By.XPATH, '//label[contains(text(), "Demandeur")]/following::input[@type="checkbox"]')           
        Demandeur.click()
        time.sleep(1)

    #cocher la case "pas de controle annuaire"
    if data["ctr_annuaire"]==True:
        ctr_annuaire = driver.find_element(By.XPATH, '//label[contains(text(), "Pas de contrôle annuaire")]/following::input[@type="checkbox"]')
        ctr_annuaire.click()


    time.sleep(1)


    if data["mail"]!="":
        mail = driver.find_element(By.XPATH, '//label[contains(text(), "Adresse mail Workflow")]/following::input[@type="text"]')
        mail.send_keys(data["mail"])
        time.sleep(1)

    if data["telephone"]!="":
        telephone = driver.find_element(By.XPATH, '//label[contains(text(), "Téléphone par défaut")]/following::input[@type="text"]')
        telephone.send_keys(data["telephone"])
        time.sleep(1)

    if data["fax"]!="":
        fax = driver.find_element(By.XPATH, '//label[contains(text(), "Fax par défaut")]/following::input[@type="text"]')
        fax.send_keys(data["fax"])
        time.sleep(1)

    if data["Accès"]!="":
        
        Accès = driver.find_element(By.XPATH, '//label[contains(text(), "Accès")]/following::input[@type="text"]')
        Accès.send_keys(data["Accès"])
        time.sleep(1)
    
    if data["identif"]!="":
        identif = driver.find_element(By.XPATH, '//label[contains(text(), "Identif. connexion")]/following::input[@type="text"]')
        identif.send_keys(data["identif"])
        time.sleep(1)

    if data["fonction"]!="":
        fonction = driver.find_element(By.XPATH, '//label[contains(text(), "Fonction")]/following::input[@type="text"]')
        fonction.send_keys(data["fonction"])
        time.sleep(1)

    if data["cod-metier"]!="":
        cod_metier = driver.find_element(By.XPATH, '//label[contains(text(), "Code métier")]/following::input[@type="text"]')
        cod_metier.send_keys(data["cod_metier"])
        time.sleep(1)

    if data["Profil_menu"]!="":
        Profil_menu = driver.find_element(By.XPATH, '//label[contains(text(), "Profil menu")]/following::input[@type="text"]')
        Profil_menu.send_keys(data["Profil_menu"])
        time.sleep(1)

    if data["Profil_fonction"]!="":
        Profil_fonction = driver.find_element(By.XPATH, '//label[contains(text(), "Profil fonction")]/following::input[@type="text"]')
        Profil_fonction.send_keys(data["Profil_fonction"])
        time.sleep(1)


    button_create = driver.find_element(By.XPATH, '//*[@id="s_app_body"]/div/article/div[2]/header/div[1]/div/div[4]/div/div[1]/div[3]/a/div')
    button_create.click()

    input("Test terminé. Appuyez sur Entrée pour fermer le navigateur...")








