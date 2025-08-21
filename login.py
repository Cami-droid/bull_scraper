import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils import wait_for_element # Asegúrate de importar la función


def perform_login(driver, username, password, login_url):
    try:
        driver.get(login_url)
        print("🌍 Navegando a la página de login...")
        
        # 🟢 REEMPLAZAMOS time.sleep(2) con espera explícita
        # Espera a que el campo de email esté visible y listo
        user_input = wait_for_element(driver, (By.ID, "Email"))
        
        if not user_input:
            print("❌ No se encontró el campo de usuario 'Email'.")
            return None
            
        # Espera a que el campo de contraseña esté visible
        pass_input = wait_for_element(driver, (By.ID, "Password"))
        
        if not pass_input:
            print("❌ No se encontró el campo de contraseña 'Password'.")
            return None

        user_input.clear()
        user_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)

        # 🟢 REEMPLAZAMOS driver.find_element(By.ID, "submitButton")
        # con espera explícita para que el botón sea clickeable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submitButton"))
        )
        
        login_button.click()

        # 🟢 REEMPLAZAMOS time.sleep(3) con una espera inteligente
        # Espera a que la URL cambie para confirmar que el login fue exitoso
        WebDriverWait(driver, 20).until(EC.url_changes(login_url))
        print("✅ Login exitoso. URL actual:", driver.current_url)
        
        cookies = driver.get_cookies()
        return cookies

    except Exception as e:
        print(f"❌ Fallo en el proceso de login: {e}")
        
        # Opcional: El código de depuración que tenías es muy útil, lo mantengo.
        debug_path = os.path.join(os.getcwd(), "debug_login_fail.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 HTML de login fallido guardado en: {debug_path}")
        
        return None