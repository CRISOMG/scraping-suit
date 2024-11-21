import json
from scraper import sum_times
from scraper import fomat_total_time

data = {}

with open("data.v1.json", "r") as j:
    data = json.load(j)


total_seconds = 0
total_lessons = 0
total_time = []
for l_path in data.values():
    for course in l_path['courses'].values(): 
        total_time += course['time']
        total_lessons += course["qty"]
        (h,m,s,ts) = fomat_total_time(total_time)
        total_seconds += ts
        pass
    pass

(h,m,s,ts) = fomat_total_time(total_time)

print(f"{h}H {m}m {s}s")
print(f"total courses: {total_lessons}")
print(f"h by courses {total_lessons / h}")
