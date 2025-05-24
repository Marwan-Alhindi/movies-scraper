from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_movies_with_showtimes(day_text="24 May"):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://www.muvicinemas.com/en/movie-finder")

        # 1) City select
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[.='Riyadh']"))).click()
            driver.find_element(By.XPATH, "//button[.='Select']").click()
            print("✅ Selected Riyadh")
            time.sleep(3)
        except:
            print("ℹ️ City popup skipped")

        # 2) Pick date
        for btn in driver.find_elements(By.CSS_SELECTOR, '[id^="movie-day-"]'):
            spans = btn.find_elements(By.TAG_NAME, "span")
            if len(spans) >= 3:
                date_str = f"{spans[1].text.strip()} {spans[2].text.strip()}"
                if date_str.lower() == day_text.lower():
                    btn.click()
                    print(f"✅ Selected day: {date_str}")
                    break
        time.sleep(3)

        # 3) All Day
        for div in driver.find_elements(By.CSS_SELECTOR, 'div[class*="MuiBox-root"]'):
            if "all day" in div.text.lower():
                driver.execute_script("arguments[0].click()", div)
                print("✅ Clicked All Day")
                break
        time.sleep(3)

        # 4) Show Results
        show_btn = wait.until(EC.element_to_be_clickable((By.ID, "show-results-button")))
        driver.execute_script("arguments[0].click()", show_btn)
        print("✅ Clicked Show Results")
        time.sleep(3)

        # 5) Scroll to load all movies
        last_h = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

        # — PASS 1: collect static info
        movies = []
        summaries = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")
        print(len(summaries), "movies found")
        for summary in summaries:
            title = summary.find_element(By.CSS_SELECTOR, "h1.MuiTypography-body1").text.strip()
            genres = [g.text for g in summary.find_elements(By.CSS_SELECTOR, ".MuiTypography-body1.css-1kdi5wt")]

            drl = summary.find_element(By.CSS_SELECTOR, "p.MuiTypography-body1.css-dmydkl").text.strip()
            duration = rating = language = ""
            for part in [p.strip() for p in drl.split(" . ") if p.strip()]:
                if "h" in part.lower() and any(c.isdigit() for c in part):
                    duration = part
                elif any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
                    rating = part
                else:
                    language = part

            movies.append({
                "title":        title,
                "genres":       genres,
                "duration":     duration,
                "rating":       rating,
                "language":     language,
                "show_details": []
            })

            # # print PASS 1 info
            # print("PASS 1")
            # print("==========================")
            # print(movies[0])
        # — PASS 2: for each movie, expand and grab only the location names
        for idx in range(len(movies)):
            summary = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")[idx]
            driver.execute_script("arguments[0].scrollIntoView(true);", summary)
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(0.8)

            collapse = summary.find_element(
                By.XPATH,
                "./following-sibling::div[contains(@class,'MuiCollapse-root')]"
            )
            details = collapse.find_element(By.CSS_SELECTOR, ".MuiAccordionDetails-root")

            locs = []
            for loc_group in details.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-6z6qye"):
                try:
                    name = loc_group.find_element(By.CSS_SELECTOR, "p.css-zgk7x3").text.strip()
                except:
                    name = "Unknown"
                locs.append(name)
            movies[idx]["locations"] = locs

            # collapse back
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(0.4)

        # print("ℹ️ PASS 2 done: locations collected")
        # # print PASS 2 info
        # print("PASS 2")
        # print("==========================")
        # print(movies[0])
        # print(movies)
        # — PASS 3: for each movie and each location, expand and grab cinema & times
        for idx in range(len(movies)):
            summary = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")[idx]
            driver.execute_script("arguments[0].scrollIntoView(true);", summary)
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(0.8)

            collapse = summary.find_element(
                By.XPATH,
                "./following-sibling::div[contains(@class,'MuiCollapse-root')]"
            )
            details = collapse.find_element(By.CSS_SELECTOR, ".MuiAccordionDetails-root")
            # We want to know three things:
            # 1. summary - Summary is literally the box that contains the movie title, generes, rating, language and time
            # 2. collapse - there seems to be no difference between collapse and details
            # 3. details - there seems to be no difference between collapse and details

            # print("Summary:")
            # print(summary)
            # print(summary.text)
            # print("Collapse:")
            # print(collapse)
            # print(collapse.text)
            # print("Details:")
            # print(details)
            # print(details.text)
            
            # PASS 3 – extract every “Read More” ↔ times chunk from collapse.text
            lines = collapse.text.splitlines()

            locs = movies[idx]["locations"]
            # find the line‐indices of each location name
            loc_indices = [i for i, L in enumerate(lines) if L in locs]

            times_per_loc = {}
            for i, loc in enumerate(locs):
                start = loc_indices[i]
                end   = loc_indices[i+1] if i+1 < len(loc_indices) else len(lines)
                segment = lines[start+1:end]

                # now split that segment by “Read More” markers
                exp_times = []
                current   = []
                for line in segment:
                    if line == "Read More":
                        if current:
                            exp_times.append(current)
                        current = []
                    elif "AM" in line or "PM" in line:
                        current.append(line)
                if current:
                    exp_times.append(current)

                times_per_loc[loc] = exp_times

            # attach to movies
            movies[idx]["show_details"] = [
                {"location": loc, "times": times_per_loc.get(loc, [])}
                for loc in locs
            ]

        # # print PASS 1 info
        # print("PASS 3")
        # print("==========================")
        # print(movies[0])

        # — PASS 4: for each movie, grab cinema names and merge with PASS 3 times
        for idx in range(len(movies)):
            # build a map of location → times from PASS 3
            times_map = {
                entry["location"]: entry["times"]
                for entry in movies[idx]["show_details"]
            }

            # 1) scroll up & re-open this movie
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.3)
            summary = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")[idx]
            driver.execute_script("arguments[0].scrollIntoView(true);", summary)
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(0.8)

            # 2) grab its details panel
            collapse = summary.find_element(
                By.XPATH,
                "./following-sibling::div[contains(@class,'MuiCollapse-root')]"
            )
            details = collapse.find_element(By.CSS_SELECTOR, ".MuiAccordionDetails-root")

            new_show = []
            loc_groups = details.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-6z6qye")

            # 3) for each location, click each Read More to get the NAMES
            for loc_name, lg in zip(movies[idx]["locations"], loc_groups):
                cinema_names = []
                for link in lg.find_elements(By.CSS_SELECTOR, "a.css-scsw1e"):
                    # click via JS
                    driver.execute_script("arguments[0].click()", link)
                    dialog = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                    name = dialog.find_element(By.CSS_SELECTOR, "h4.css-1n9xlo3").text.strip()
                    # close via JS
                    close_btn = dialog.find_element(By.XPATH, ".//button")
                    driver.execute_script("arguments[0].click()", close_btn)
                    wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                    cinema_names.append(name)

                # 4) zip names with the times list for this location
                times_list = times_map.get(loc_name, [])
                entries = [
                    {"cinema": cn, "times": times_list[i] if i < len(times_list) else []}
                    for i, cn in enumerate(cinema_names)
                ]

                new_show.append({
                    "location": loc_name,
                    "cinema":   entries
                })

            # 5) replace the old show_details and collapse back
            movies[idx]["show_details"] = new_show
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(0.4)

        # print("PASS 4 complete: cinema names merged with PASS 3 times")
        # print(movies[0])
        return movies
    finally:
        driver.quit()


if __name__ == "__main__":
    import pprint
    data = get_movies_with_showtimes("24 May")
    pprint.pprint(data)