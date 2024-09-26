from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import json
from utils import fomat_total_time

def main_logic():
        
    hrefs = {}
    data = {}

    with open("data.json", "r") as j:
        data = json.load(j)
    with open("hrefs.json", "r") as j:
        hrefs = json.load(j)

    try:
        user_data_dir = "C:/Users/cristian/AppData/Local/Google/Chrome/User Data"
        profile_dir = "Default" 
        chrome_options = Options()
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory={profile_dir}")
        chrome_options.add_argument(
            "--remote-debugging-port=9222"
        ) 
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        service = Service(
            log_path="C:/Users/Cristian/OneDrive/Desktop/Python/chromedriver.log",
            verbose=True,
        )
        driver = webdriver.Chrome(service=service, options=chrome_options)

        wait = WebDriverWait(driver, 10)

        def wait_for_DOM_load():
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

        # Example: Navigate to Google
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[1::][-1])
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        driver.get("https://platzi.com/escuela/ingles/")

        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "section > div > div > div > div > a")
            )
        )

        english_learning_paths = driver.execute_script(
            "return document.querySelectorAll('section > div > div > div > div > a');"
        )
        english_learning_paths_href = [
            learning_path.get_attribute("href") for learning_path in english_learning_paths
        ]
        total_lessons = 0
        total_time = []
        for learning_path_href in english_learning_paths_href:

            already_completed_recollection = hrefs.get(learning_path_href, {}).get('completed_recollection')
            if already_completed_recollection:
                continue

            driver.execute_script(f"window.open('{learning_path_href}', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
     
            print(f"{learning_path_href}")

            course_selector = "div > div > div > div > div > div.Tabs > div.Tabs-content > div > div > div > a"

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, course_selector)))

            learning_path_title = driver.execute_script(
                f"return document.querySelector('h1')?.innerText"
            )
            learning_path_courses = driver.execute_script(
                f"return document.querySelectorAll('{course_selector}');"
            )
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
                driver.execute_script(f"window.open('{course_href}', '_blank');")
                driver.switch_to.window(driver.window_handles[2::][-1])
            
                WebDriverWait(driver, 90).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".Hero-content-title"))
                )
                time.sleep(1)

            tabs = list(driver.window_handles[2::])
            switch_to_handled_tabs = lambda i: driver.switch_to.window(tabs[i])
            for i, tab in enumerate(tabs):
                print(
                    f"driver_model: {len(driver.window_handles[2::])} tabs: {len(tabs)} index: {i}"
                )
                switch_to_handled_tabs(i)  # Switch back to the learning path tab
                # wait_for_DOM_load()

                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".Hero-content-title"))
                )
                couse_title = driver.execute_script(
                    "return document.querySelector('.Hero-content-title').innerText"
                )

                course_href = driver.execute_script('return window.location.href')
                js_get_lessons_qty = f"return document.querySelectorAll('ul.ContentBlock-list > li.ContentBlock-list-item a.ContentClass-item-link').length"
                js_get_lessons_time = f"return [...document.querySelectorAll('ul.ContentBlock-list > li.ContentBlock-list-item a.ContentClass-item-link div.ContentClass-item-content > p')].map((el)=> el.innerText)"
                
                lessons_qty = driver.execute_script(js_get_lessons_qty)
                lessons_time = driver.execute_script(js_get_lessons_time)
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
        driver.quit()


if __name__ == '__main__':
    main_logic()