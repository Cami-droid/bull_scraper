from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def perform_login(driver, username, password, login_url):
    try:
        driver.get(login_url)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "Email"))).send_keys(username)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "Password"))).send_keys(password)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "submitButton"))).click()
        WebDriverWait(driver, 30).until(EC.url_contains("/Clients/Dashboard"))
        return driver.get_cookies()
    except TimeoutException:
        return None
