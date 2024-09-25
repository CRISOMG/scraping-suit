from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import json

data = {}

with open('data.json', 'r') as j:
  data = json.load(j)



# Define the path to the ChromeDriver executable
try:
    # Define the path to the Chrome user data
    user_data_dir = 'C:/Users/cristian/AppData/Local/Google/Chrome/User Data'
    profile_dir = 'Default'  # Cambia esto al perfil que deseas usar (ej., "Default")

    # Create Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"profile-directory={profile_dir}")
    chrome_options.add_argument("--remote-debugging-port=9222")  # Change the port if needed
    chrome_options.add_argument("--no-sandbox")  # Overcome sandbox issues
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument('--ignore-certificate-errors')
    # Create a Service object for ChromeDriver
    service = Service(log_path='C:/Users/Cristian/OneDrive/Desktop/Python/chromedriver.log', verbose=True)
    # Initialize the WebDriver with the specified options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    wait = WebDriverWait(driver, 10)

    def wait_for_DOM_load():
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
  

    
    # Example: Navigate to Google
    driver.get('https://platzi.com/escuela/ingles/')

    # 'section > div > div > div > div > a'

    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'section > div > div > div > div > a'))
    )
    
    english_learning_paths = driver.execute_script("return document.querySelectorAll('section > div > div > div > div > a');")
    english_learning_paths_href = [learning_path.get_attribute('href') for learning_path in english_learning_paths]
    
    for learning_path_href in english_learning_paths_href:
        data['english_learning_paths_href'][learning_path_href] = {
            'courses_hrefs': {}, 
            'completed_recollection': False, 
        }
        
        # Open each learning path in a new tab or navigate directly
        driver.execute_script(f"window.open('{learning_path_href}', '_blank');")
        driver.switch_to.window(driver.window_handles[1])
        # driver.get(learning_path_href)
        # wait_for_DOM_load()  # Ensure the page has fully loaded
        print(f'{learning_path_href}')
       
        # Selector for the individual courses in the learning path
        course_selector = 'div > div > div > div > div > div.Tabs > div.Tabs-content > div > div > div > a'

        # Wait for the courses to load in the learning path
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, course_selector))
        )

        learning_path_title = driver.execute_script(f"return document.querySelector('h1')?.innerText")
        learning_path_courses = driver.execute_script(f"return document.querySelectorAll('{course_selector}');")
        course_hrefs = [course.get_attribute('href') for course in learning_path_courses]
        data[learning_path_href]['courses_hrefs'] = {course_href: False for course_href in course_hrefs}

        # Iterate through each course in the learning path
        
        data[learning_path_title] = {
            'path': learning_path_href,
            'title': learning_path_title,
            'courses': {},
            'courses_qty': len(course_hrefs),
            'total-lessons': 0
        }
        for course_href in course_hrefs:
            # Navigate to the course
            data['english_learning_paths_href'][learning_path_href]['courses_hrefs'][course_href] = course_hrefs

            print(f'    {course_href}')
            # driver.get(course_href)asyncio
            driver.execute_script(f"window.open('{course_href}', '_blank');")
            driver.switch_to.window(driver.window_handles[2::][-1])
            # wait.until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, '.Hero-content-title'))
            # )
            WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".Hero-content-title"))
             )
            time.sleep(1)
        
        tabs = list(driver.window_handles[2::])
        switch_to_handled_tabs = lambda i: driver.switch_to.window(tabs[i])
        for i, tab in enumerate(tabs):
            print(f'driver_model: {len(driver.window_handles[2::])} tabs: {len(tabs)} index: {i}')
            switch_to_handled_tabs(i)  # Switch back to the learning path tab
            # wait_for_DOM_load()

            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.Hero-content-title'))
            )
            couse_title = driver.execute_script("return document.querySelector('.Hero-content-title').innerText")

            js_get_lessons_qty = f"return document.querySelectorAll('ul.ContentBlock-list > li.ContentBlock-list-item a.ContentClass-item-link').length"
            lessons_qty = driver.execute_script(js_get_lessons_qty)
            print(f'{couse_title}: {lessons_qty}')
            data[learning_path_title]['courses'][couse_title] = {
                'title':couse_title,
                'qty': lessons_qty,
                'path':  course_href
            }
            data[learning_path_title]['total-lessons'] += lessons_qty 
            driver.close()


        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])



    # print(elements)
    # Print the title of the page
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the driver safely
    # driver.quit()
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)
