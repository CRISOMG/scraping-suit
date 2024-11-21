from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import json
from utils import extract_function, fomat_total_time
from typing import Dict, Tuple, Any



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
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--remote-debugging-port=9222") 
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    service = Service(
        log_path="C:/Users/Cristian/OneDrive/Desktop/Python/chromedriver.log",
        verbose=True,
    )
    driver = webdriver.Chrome(service=service, options=chrome_options)

    wait = WebDriverWait(driver, 10)

    return (driver,wait)

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

def safe_execute_script(driver,wait,script, element_to_await_css_selector = None):
    try:
        if (element_to_await_css_selector):
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, element_to_await_css_selector)
                )
            )
        js_data = driver.execute_script(script)
        return js_data
    except Exception as e:
        raise CustomError(f"error executing {script}")

def safe_execute_querySelectorAll_script(driver,wait,selector):
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, selector)
        )
    )
    js_data = driver.execute_script(
        f"return document.querySelectorAll('{selector}');"
    )

    return js_data

def main_logic():

    try:

        js_scripts = load_js_scripts()

        data, hrefs = persistence()
        
        (driver,wait) = configure_utils()

        enrich_js_strin_code_from_python = extract_function(js_scripts,"js_script_2")
        js_rich_string_code = enrich_js_strin_code_from_python("'hola'")
        print(js_rich_string_code)
        result = safe_execute_script(driver, wait, js_rich_string_code)
        print(result)


        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1::][-1])
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        driver.get("https://platzi.com/escuela/ingles/")

        learding_paths_of_platzi_english_school_selector = 'section > div > div > div > div > a'
        english_learning_paths = safe_execute_querySelectorAll_script(driver, wait, learding_paths_of_platzi_english_school_selector)

        english_learning_paths_href = [
            learning_path.get_attribute("href") for learning_path in english_learning_paths
        ]
        total_lessons = 0
        total_time = []
        for learning_path_href in english_learning_paths_href:

            already_completed_recollection = hrefs.get(learning_path_href, {}).get('completed_recollection')
            if already_completed_recollection:
                continue

            js_do_open_learing_path =f"window.open('{learning_path_href}', '_blank');"
            safe_execute_script(driver, wait, js_do_open_learing_path)
            driver.switch_to.window(driver.window_handles[1])
     
            print(f"{learning_path_href}")

           
            js_get_learning_path_title =f"return document.querySelector('h1')?.innerText"
            learning_path_title = safe_execute_script(driver, wait, 
                js_get_learning_path_title
            )
            course_selector = "div > div > div > div > div > div.Tabs > div.Tabs-content > div > div > div > a"
            learning_path_courses = safe_execute_querySelectorAll_script(driver,wait,course_selector)
            
            course_hrefs = [
                course.get_attribute("href") for course in learning_path_courses
            ]

            hrefs = {
                **hrefs,
                learning_path_href: {
                    "courses_hrefs": {course_href: hrefs.get(learning_path_href,{}).get('courses_hrefs',{}).get(course_href, False) for course_href in course_hrefs},
                    "completed_recollection": False,
                },
            }

            data[learning_path_title] = {
                "path": learning_path_href,
                "title": learning_path_title,
                "courses": {},
                "courses_qty": len(course_hrefs),
                "total-lessons": 0,
            }

            for course_href in course_hrefs:
                already_checked = hrefs.get(learning_path_href,{}).get('courses_hrefs',{}).get(course_href, False)
                if already_checked:
                    continue

                # challenge-form
                js_do_open_course = f"window.open('{course_href}', '_blank');"
                safe_execute_script(driver, wait, js_do_open_course)
                driver.switch_to.window(driver.window_handles[2::][-1])
                # WebDriverWait(driver, 90).until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, ".Hero-content-title"))
                # )
                time.sleep(1)

            tabs = list(driver.window_handles[2::])
            switch_to_handled_tabs = lambda i: driver.switch_to.window(tabs[i])
            for i, tab in enumerate(tabs):
                print(
                    f"driver_model: {len(driver.window_handles[2::])} tabs: {len(tabs)} index: {i}"
                )
                switch_to_handled_tabs(i)  
             

               
                js_get_course_hero_title = "return document.querySelector('.Hero-content-title').innerText"
                couse_title = safe_execute_script(driver, wait, js_get_course_hero_title,".Hero-content-title")

                course_href = driver.current_url
                js_get_lessons_qty = f"return document.querySelectorAll('ul.ContentBlock-list > li.ContentBlock-list-item a.ContentClass-item-link').length"
                js_get_lessons_time = f"return [...document.querySelectorAll('ul.ContentBlock-list > li.ContentBlock-list-item a.ContentClass-item-link div.ContentClass-item-content > p')].map((el)=> el.innerText)"
                lessons_qty = safe_execute_script(driver, wait, js_get_lessons_qty)
                lessons_time = safe_execute_script(driver, wait, js_get_lessons_time)
                total_time += lessons_time
                (h,m,s,ts) = fomat_total_time(lessons_time)

                data[learning_path_title]["courses"][couse_title] = {
                    "title": couse_title,
                    "qty": lessons_qty,
                    "time": lessons_time,
                    "total_time": f"{h}H {m}m {s}s",
                    "path": course_href,
                }
                data[learning_path_title]["total-lessons"] += lessons_qty
                total_lessons += lessons_qty
                with open("total-lessons.txt", "w") as file:
                    file.write(str(total_lessons))
                with open("total-time.txt", "w+") as file:
                    before_time = file.read() or 0
                    (h,m,s,ts) = fomat_total_time(total_time)
                    file.write(f"{ts + int(before_time)}")
                hrefs[learning_path_href]["courses_hrefs"][course_href]= True
                driver.close()

            hrefs[learning_path_href]['completed_recollection'] = True

            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:

        with open("hrefs.json", "w") as json_file:
            json.dump(hrefs, json_file, indent=2)
        with open("data.json", "w") as json_file:
            json.dump(data, json_file, indent=2)


if __name__ == '__main__':
    main_logic()