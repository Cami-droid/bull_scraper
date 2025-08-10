from selenium.webdriver.common.by import By
import time
import os

def perform_login(driver, username, password, login_url):
    driver.get(login_url)
    time.sleep(2)  # Espera que cargue la página

    try:
        # Campo de usuario ahora es "Email"
        user_input = driver.find_element(By.ID, "Email")
        pass_input = driver.find_element(By.ID, "Password")

        user_input.clear()
        user_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)

        # Click en el botón con id "submitButton"
        login_button = driver.find_element(By.ID, "submitButton")
        login_button.click()

        time.sleep(3)  # Espera que cargue el dashboard

        # Verificamos si el login fue exitoso
        if "Dashboard" in driver.page_source or "Resumen" in driver.page_source:
            print("✅ Login exitoso.")
            return driver.get_cookies()
        else:
            raise Exception("No se detectaron elementos del dashboard tras login.")

    except Exception as e:
        print(f"❌ Login fallido: {e}")

        # Guardar HTML de depuración
        debug_path = os.path.join(os.getcwd(), "debug_login_fail.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"💾 HTML de login fallido guardado en: {debug_path}")

        return None
