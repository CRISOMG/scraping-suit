from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import json
from utils import extract_function, fomat_total_time, is_element_present, wait_until_by_xpath
from typing import Dict, Tuple, Any
from selenium.common.exceptions import NoSuchElementException


def wait_for_DOM_load(driver):
    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def configure_utils():
    user_data_dir = "C:/Users/cristian/AppData/Local/Google/Chrome/User Data"
    profile_dir = "Default"
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"profile-directory={profile_dir}")
    # chrome_options.add_argument("--incognito")
    # chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    service = Service(
        log_path="C:/Users/Cristian/OneDrive/Desktop/Python/chromedriver.log",
        verbose=True,
    )
    driver = webdriver.Chrome(service=service, options=chrome_options)

    wait = WebDriverWait(driver, 60*10)

    return (driver, wait)


TPersistenceReturn = Tuple[Dict[str, Any], Dict[str, Any]]


def persistence():
    hrefs = {}
    data = {}

    with open("data.json", "r") as j:
        data = json.load(j)
    with open("hrefs.json", "r") as j:
        hrefs = json.load(j)

    return data, hrefs


def load_js_scripts():
    js = Any

    with open("scripts.js", "r") as js_file:
        js = js_file.read()
    return js


class CustomError(Exception):
    def __init__(self, message):
        super().__init__(message)


def safe_execute_script(driver, wait, script, element_to_await_css_selector=None):
    try:
        if element_to_await_css_selector:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, element_to_await_css_selector)
                )
            )
        js_data = driver.execute_script(script)
        return js_data
    except Exception as e:
        raise CustomError(f"error executing {script}")


def safe_execute_querySelectorAll_script(driver, wait, selector):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    js_data = driver.execute_script(f"return document.querySelectorAll('{selector}');")

    return js_data


def main_logic():

    try:

        js_scripts = load_js_scripts()

        data, hrefs = persistence()

        (driver, wait) = configure_utils()

        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1::][-1])
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        driver.get("https://www.duolingo.com/practice-hub/words")
        # XPath strings
        li_elements_xpath = (
            '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div/section[2]/ul/li'
        )
        next_button_xpath = '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div/section[2]/ul/li[@role="button"]'
        next_button_loading_xpath = '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div/section[2]/ul/li[@role="button"]/div'
        word_data_xpath = '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div/section[2]/ul/li/div/div/div'
        words_xpath = (
            '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div/section[2]/div/div[1]/h2'
        )

        # Get all list items
        wait_until_by_xpath(driver,wait,words_xpath)
        wait_until_by_xpath(driver,wait,li_elements_xpath)
        uls = len(driver.find_elements(By.XPATH, li_elements_xpath))
        # Get the word count from the heading
        words_text = driver.find_element(By.XPATH, words_xpath).text
        words = int(words_text.split(" ")[0])

        # Find the first list item with the role="button"
        next_button_element = driver.find_element(By.XPATH, next_button_xpath)

        # //*[@id="root"]/div[2]/div/div[3]/div/div[2]/div/section[2]/ul/li/div
        # Check if the first child is a <b> tag and click if true
        while uls < words:
            if is_element_present(driver, next_button_xpath):
                next_button_element.location_once_scrolled_into_view
                next_button_element.click()
            
            if is_element_present(driver, next_button_loading_xpath):
                wait.until(EC.presence_of_element_located((By.XPATH, f"{next_button_xpath}/b")))

            uls = len(driver.find_elements(By.XPATH, li_elements_xpath))
            print(f'{uls}')

        elements = driver.find_elements(By.XPATH, word_data_xpath)

        htmls = [element.get_attribute('innerHTML') for element in elements]
        with open('diolingo_words.json','w') as file:
            json.dump(htmls, file, indent=2)


    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pass


if __name__ == "__main__":
    main_logic()
