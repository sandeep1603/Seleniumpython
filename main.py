from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

LOGIN_URL = 'https://www.dtvp.de/Center/company/login.do'
SEARCH_URL = 'https://www.dtvp.de/Center/company/announcements/categoryOverview.do?method=showCategoryOverview'
USERNAME = 'info@wildstyle-network.com'
PASSWORD = 'Wildstyle01'
KEYWORDS = [
    "Akzeptanzkampagne", "Animation", "Bewegtbild", "Corporate-Design", "Coporatedesign", "Design",
    "Film", "Gemeinschaftskampagne", "Gesundheits-Kampagne", "Gesundheitskampagne",
    "Informations-Kampagne", "Informationskampagne", "Kampagne", "Kommunikationskampagne",
    "Kommunikationsmaßnahmen", "Kommunikationsstrategie", "Marketingagentur",
    "Marketingmaßnahmen", "Markenentwicklung", "Onlinekommunikation", "Organisationsmanagement",
    "PR-Kampagne", "Produktentwicklung", "Prozessmanagement", "Social Media", "Social-Media",
    "Socialmedia", "Video", "Websiterelaunch", "\u00d6ffentlichkeits-Kampagne", "\u00d6ffentlichkeitskampagne"
]

def init_browser():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def handle_cookie_consent(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Alles akzeptieren')]")))
        driver.find_element(By.XPATH, "//button[contains(text(), 'Alles akzeptieren')]").click()
        print("Cookie consent accepted.")
    except:
        print("No cookie consent popup detected or already handled.")

def login(driver):
    print("Navigating to login page...")
    driver.get(LOGIN_URL)
    handle_cookie_consent(driver)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login")))
        print("Filling login form...")
        driver.find_element(By.NAME, "login").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)

        try:
            # Click the <input type="submit"> with value 'Senden'
            driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Senden']").click()
        except Exception as e:
            print("Failed to click the login button:", e)
            driver.find_element(By.NAME, "login_form").submit()


        WebDriverWait(driver, 10).until(EC.url_changes(LOGIN_URL))
        print("Login successful.")
    except Exception as e:
        print("Login failed or element not found:", e)
        input("\nPress Enter to keep browser open and debug manually...")
        raise

def search_tenders(driver, keyword):
    print(f"Searching tenders for: {keyword}")
    try:
        driver.get(SEARCH_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search_input")))

        search_box = driver.find_element(By.ID, "search_input")
        search_box.clear()
        search_box.send_keys(keyword)

        driver.find_element(By.ID, "search_button").click()
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tender-result")))

        results = driver.find_elements(By.CLASS_NAME, "tender-result")
        print(f"Found {len(results)} results for '{keyword}'")

        for result in results:
            link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.get(link)

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tender-details")))
            title = driver.find_element(By.ID, "tender-title").text
            deadline = driver.find_element(By.ID, "tender-deadline").text
            print(f"\nTitle: {title}\nDeadline: {deadline}\n")

            driver.back()
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tender-result")))
    except Exception as e:
        print(f"Error while searching '{keyword}':", e)
        input("\nPress Enter to debug...")
        raise

def manual_url_export(driver):
    print("\n=== HTML Export Mode ===")
    target_url = input("Paste your logged-in search result URL here: ").strip()
    if not target_url:
        print("No URL provided. Skipping export.")
        return
    print("Navigating to your provided URL...")
    driver.get(target_url)
    time.sleep(3)
    with open("dtvp_export.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved page as dtvp_export.html")

def main():
    driver = init_browser()
    try:
        login(driver)
        for keyword in KEYWORDS:
            search_tenders(driver, keyword)
        manual_url_export(driver)
    except Exception as e:
        print("Unhandled exception:", e)
    finally:
        print("\nAll done. Keeping browser open for review.")
        input("\nPress Enter to close browser...")
        driver.quit()

if __name__ == '__main__':
    main()
