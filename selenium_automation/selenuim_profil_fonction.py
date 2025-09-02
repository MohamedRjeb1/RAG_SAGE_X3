from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


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

try:
    menu2 = driver.find_element(By.ID, "ce66f85d-5874-499f-9e8c-1f3f2e940440")
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

# 4. Saisie et attente sans sleep
code_input = wait.until(
    EC.visibility_of_element_located((By.XPATH, '//label[contains(text(), "Code profil")]/following::input[@type="text"]'))
)
code_input.send_keys("STGIA")









input("Test terminé. Appuyez sur Entrée pour fermer le navigateur...")
driver.quit()








