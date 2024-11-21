import re

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
    # Regular expression to find the specific function
    pattern = rf"function {function_name}\s*\(.*?\)\s*{{.*?}}"
    match = re.search(pattern, js_code, re.DOTALL)  # re.DOTALL allows '.' to match newlines
    
    if match:
        js_fn_str = match.group(0)  # Return the entire matched function
        return lambda py_params = '': f"{js_fn_str} \n return {function_name}({py_params})"
    else:
        return None  # Function not found
