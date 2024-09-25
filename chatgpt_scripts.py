# Initialize a dictionary to hold the learning paths and their corresponding courses
data = {}

# Gather learning paths and initialize the inner dictionary
for learning_path in english_learning_paths:
    learning_path_href = learning_path.get_attribute('href')
    logging.info(f'Processing: {learning_path_href}')

    # Initialize the inner dictionary for courses
    data[learning_path_href] = {'courses_hrefs': {}, 'completed_recollection': False}

    # Open the learning path
    driver.get(learning_path_href)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div > div > div > div > div > div.Tabs > div.Tabs-content > div > div > div > a')))

    learning_path_title = driver.find_element(By.TAG_NAME, 'h1').text
    course_hrefs = [course.get_attribute('href') for course in driver.find_elements(By.CSS_SELECTOR, 'div > div > div > div > div > div.Tabs > div.Tabs-content > div > div > div > a')]

    # Update the learning path data with course hrefs
    data[learning_path_href]['courses_hrefs'] = {course_href: {} for course_href in course_hrefs}

    # Now you can continue processing the courses as needed
    data[learning_path_title] = {
        'path': learning_path_href,
        'title': learning_path_title,
        'courses': {},
        'courses_qty': len(course_hrefs),
        'total-lessons': 0
    }

# You can now access `learning_paths_dict` which has your desired structure
