from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# lists of city names in English and Arabic
CITIES = [
    ("Riyadh",       "الرياض"),
    ("Jeddah",       "جدة"),
    ("Dhahran",      "الظهران"),
    ("Dammam",       "الدمام"),
    ("Al Hofuf",     "الهفوف"),
    ("Al Jubail",    "الجبيل"),
    ("Buraydah",     "بريدة"),
    ("Unayzah",      "عنيزة"),
    # ("Taif",         "الطائف"),
    # ("Khamis Mushait","خميس مشيط"),
]

def get_movies_for_city(day_text, city_en, city_ar):
    # ————— set up Chrome with notifications disabled —————
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # disable the push‐notification bar
    options.add_argument("--disable-notifications")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 15)
    movies = []

    try:
        # ——————————————
        # 1) load the EN finder and pick the city
        driver.get("https://www.muvicinemas.com/en/movie-finder")

        # wait for the city‐picker dialog title to show
        wait.until(EC.visibility_of_element_located((By.ID, "cities-title")))

        # locate the <label> whose nested text is exactly our English city name
        label_xpath = f"//label[.//div[text()='{city_en}']]"
        wait.until(EC.element_to_be_clickable((By.XPATH, label_xpath))).click()

        # click the “Select” button
        wait.until(EC.element_to_be_clickable((By.ID, "city-submit"))).click()
        time.sleep(2)

        # ——————————————
        # 2) pick the date
        for btn in driver.find_elements(By.CSS_SELECTOR, '[id^="movie-day-"]'):
            spans = btn.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 3:
                if f"{spans[1].text} {spans[2].text}".lower() == day_text.lower():
                    btn.click()
                    break
        time.sleep(1)

        # 3) click “All Day”
        for div in driver.find_elements(By.CSS_SELECTOR, 'div[class*="MuiBox-root"]'):
            if "all day" in div.text.lower():
                driver.execute_script("arguments[0].click()", div)
                break
        time.sleep(1)

        # 4) show results
        show_btn = wait.until(EC.element_to_be_clickable((By.ID, "show-results-button")))
        driver.execute_script("arguments[0].click()", show_btn)
        time.sleep(2)

        # 5) scroll to load
        last_h = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

        # — PASS 1: static info
        summaries = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")
        for s in summaries:
            t = s.find_element(By.CSS_SELECTOR, "h1.MuiTypography-body1").text.strip()
            gs = [g.text for g in s.find_elements(By.CSS_SELECTOR, ".MuiTypography-body1.css-1kdi5wt")]
            drl = s.find_element(By.CSS_SELECTOR, "p.css-dmydkl").text
            dur = rate = lang = ""
            for part in [p.strip() for p in drl.split(" . ") if p.strip()]:
                if "h" in part and any(c.isdigit() for c in part):
                    dur = part
                elif any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
                    rate = part
                else:
                    lang = part
            movies.append({
                "city":         city_en,
                "title":        t,
                "genres":       gs,
                "duration":     dur,
                "rating":       rate,
                "language":     lang,
                "show_details": []
            })

        # — PASS 2/3/4: expand each movie, scrape loc→times→cinema
        for idx in range(len(movies)):
            summary = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")[idx]
            driver.execute_script("arguments[0].scrollIntoView(true);", summary)
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(1)

            collapse = summary.find_element(
                By.XPATH,
                "./following-sibling::div[contains(@class,'MuiCollapse-root')]"
            )
            details = collapse.find_element(By.CSS_SELECTOR, ".MuiAccordionDetails-root")
            lines   = collapse.text.splitlines()

            # collect location names
            loc_names = [
                lg.find_element(By.CSS_SELECTOR, "p.css-zgk7x3").text.strip()
                for lg in details.find_elements(By.CSS_SELECTOR, "div.css-6z6qye")
            ]

            # map times to each loc
            idxs = [i for i, L in enumerate(lines) if L in loc_names]
            times_map = {}
            for i, loc in enumerate(loc_names):
                seg = lines[idxs[i]+1 : (idxs[i+1] if i+1<len(idxs) else None)]
                exps = []
                cur  = []
                for L in seg:
                    if L == "Read More":
                        if cur:
                            exps.append(cur)
                        cur = []
                    elif "AM" in L or "PM" in L:
                        cur.append(L)
                if cur:
                    exps.append(cur)
                times_map[loc] = exps

            # click each Read More to get cinema names
            show_d = []
            loc_groups = details.find_elements(By.CSS_SELECTOR, "div.css-6z6qye")
            for loc, lg in zip(loc_names, loc_groups):
                cinemas = []
                for j, a in enumerate(lg.find_elements(By.CSS_SELECTOR, "a.css-scsw1e")):
                    driver.execute_script("arguments[0].click()", a)
                    dlg = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                    name = dlg.find_element(By.CSS_SELECTOR, "h4.css-1n9xlo3").text.strip()
                    driver.execute_script("arguments[0].click()", dlg.find_element(By.XPATH, ".//button"))
                    wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                    times = times_map.get(loc, [])
                    cinemas.append({
                        "cinema": name,
                        "times":  times[j] if j < len(times) else []
                    })
                show_d.append({"location": loc, "cinema": cinemas})

            movies[idx]["show_details"] = show_d

            # collapse
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(0.5)

        return movies

    finally:
        driver.quit()


if __name__ == "__main__":
    import pprint
    all_data = []
    for en, ar in CITIES:
        all_data.extend(get_movies_for_city("24 May", en, ar))
    pprint.pprint(all_data)