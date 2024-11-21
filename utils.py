import re
from typing import Any

def sum_times(time_strings):
    total_seconds = 0
    for time_str in time_strings:
        # Remove " min" and split the string
        time_str = time_str.replace(" min", "")
        minutes, seconds = map(int, time_str.split(':'))
        total_seconds += minutes * 60 + seconds
    return total_seconds

def fomat_total_time(time_strings):

    # Calculate total seconds
    total_seconds = sum_times(time_strings)

    # Convert total seconds back to hours, minutes, and seconds
    total_minutes = total_seconds // 60
    total_seconds_remainder = total_seconds % 60
    total_hours = total_minutes // 60
    total_minutes_remainder = total_minutes % 60

    return (total_hours, total_minutes_remainder, total_seconds_remainder, total_seconds)

def extract_function(js_code, function_name):
    signature_pattern = rf"function {function_name}\s*\((.*?)\)\s*{{"
    signature_match = re.search(signature_pattern, js_code, re.DOTALL)
    
    if not signature_match:
        return None  # Function signature not found
    
    params = signature_match.group(1)  # Extract the parameters
    start_index = signature_match.end()  # Start of the function body
    
    # Now, manually find the matching closing brace by tracking the brace depth
    brace_depth = 1  # We are already inside the first '{'
    end_index = start_index
    
    while brace_depth > 0 and end_index < len(js_code):
        char = js_code[end_index]
        if char == '{':
            brace_depth += 1
        elif char == '}':
            brace_depth -= 1
        end_index += 1
    
    # Extract the full function body
    function_body = js_code[start_index:end_index-1]  # Exclude the closing brace
    
    js_fn_str = f"function {function_name}({params}) {{{function_body}}}"

    return lambda py_params = '': f"{js_fn_str}\nreturn {function_name}({py_params})"


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webdriver as BaseWebDriver

def is_element_present(driver: BaseWebDriver, xpath):
    try:
        # Use find_elements, which returns a list (empty if no elements found)
        elements = driver.find_elements(By.XPATH, xpath)
        return len(elements) > 0  # True if at least one element is found
    except NoSuchElementException:
        return False  # If an exception occurs, the element is not present

from selenium.webdriver.support import expected_conditions as EC
def wait_until_by_xpath(driver: BaseWebDriver,wait,xpath):
    return wait.until(EC.presence_of_element_located((By.XPATH, xpath)), f'element not fount at\n{xpath}')