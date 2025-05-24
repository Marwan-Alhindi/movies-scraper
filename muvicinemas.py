# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# def get_movies_with_showtimes(day_text="24 May"):
#     options = Options()
#     # options.add_argument("--headless")
#     options.add_argument("--window-size=1920,1080")

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     wait = WebDriverWait(driver, 15)

#     try:
#         driver.get("https://www.muvicinemas.com/en/movie-finder")

#         # 1) City select
#         try:
#             wait.until(EC.element_to_be_clickable((By.XPATH, "//div[.='Riyadh']"))).click()
#             driver.find_element(By.XPATH, "//button[.='Select']").click()
#             print("✅ Selected Riyadh")
#             time.sleep(3)
#         except:
#             print("ℹ️ City popup skipped")

#         # 2) Pick date
#         for btn in driver.find_elements(By.CSS_SELECTOR, '[class*="MuiToggleButton-root"]'):
#             if day_text.lower() in btn.text.lower():
#                 btn.click()
#                 print(f"✅ Selected day: {btn.text}")
#                 break
#         time.sleep(3)

#         # 3) All Day
#         for div in driver.find_elements(By.CSS_SELECTOR, 'div[class*="MuiBox-root"]'):
#             if "all day" in div.text.lower():
#                 driver.execute_script("arguments[0].click()", div)
#                 print("✅ Clicked All Day")
#                 break
#         time.sleep(3)

#         # 4) Show Results
#         show_btn = wait.until(EC.element_to_be_clickable((By.ID, "show-results-button")))
#         driver.execute_script("arguments[0].click()", show_btn)
#         print("✅ Clicked Show Results")
#         time.sleep(3)

#         # 5) Scroll to load all movies
#         last_h = driver.execute_script("return document.body.scrollHeight")
#         while True:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(3)
#             new_h = driver.execute_script("return document.body.scrollHeight")
#             if new_h == last_h:
#                 break
#             last_h = new_h

#         # 6) Scrape each movie
#         movies = []
#         summaries = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")

#         for summary in summaries:
#             # — title
#             title = summary.find_element(By.CSS_SELECTOR, "h1.MuiTypography-body1").text.strip()

#             # — genres
#             genres = [g.text for g in summary.find_elements(
#                 By.CSS_SELECTOR, ".MuiTypography-body1.css-1kdi5wt"
#             )]

#             # — duration | rating | language
#             drl = summary.find_element(
#                 By.CSS_SELECTOR, "p.MuiTypography-body1.css-dmydkl"
#             ).text.strip()
#             duration = rating = language = ""
#             for part in [p.strip() for p in drl.split(" . ") if p.strip()]:
#                 if "h" in part.lower() and any(c.isdigit() for c in part):
#                     duration = part
#                 elif any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
#                     rating = part
#                 else:
#                     language = part

#             # — expand the accordion
#             driver.execute_script("arguments[0].click()", summary)
#             time.sleep(3)  # wait for the collapse to open

#             # — now find *that* movie’s collapse panel
#             collapse = summary.find_element(
#                 By.XPATH,
#                 "./following-sibling::div[contains(@class,'MuiCollapse-root')]"
#             )
#             details = collapse.find_element(By.CSS_SELECTOR, ".MuiAccordionDetails-root")

#             # — pull every location card under this details
#             show_details = []
#             for card in details.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-6z6qye"):
#                 # 1) location is the <p> right after the pin-icon figure
#                 try:
#                     loc = card.find_element(
#                         By.XPATH,
#                         ".//figure[.//img[@alt='Pin icon']]/following-sibling::p"
#                     ).text.strip()
#                 except:
#                     loc = "Unknown"

#                 # 2) times are each button#session-...
#                 times = []
#                 for btn in card.find_elements(By.XPATH, ".//button[starts-with(@id,'session-')]"):
#                     try:
#                         txt = btn.find_element(By.TAG_NAME, "p").text.strip()
#                         if txt:
#                             times.append(txt)
#                     except:
#                         pass

#                 if times:
#                     show_details.append({"location": loc, "times": times})

#             # — collapse it back
#             driver.execute_script("arguments[0].click()", summary)
#             time.sleep(3)

#             movies.append({
#                 "title":        title,
#                 "genres":       genres,
#                 "duration":     duration,
#                 "rating":       rating,
#                 "language":     language,
#                 "show_details": show_details
#             })

#         return movies

#     finally:
#         driver.quit()


# if __name__ == "__main__":
#     import pprint
#     data = get_movies_with_showtimes("24 May")
#     pprint.pprint(data)

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

        # 6) Scrape each movie
        movies = []
        summaries = driver.find_elements(By.CSS_SELECTOR, ".MuiAccordionSummary-root")

        for summary in summaries:
            # — title
            title = summary.find_element(By.CSS_SELECTOR, "h1.MuiTypography-body1").text.strip()

            # — genres
            genres = [g.text for g in summary.find_elements(
                By.CSS_SELECTOR, ".MuiTypography-body1.css-1kdi5wt"
            )]

            # — duration | rating | language
            drl = summary.find_element(
                By.CSS_SELECTOR, "p.MuiTypography-body1.css-dmydkl"
            ).text.strip()
            duration = rating = language = ""
            for part in [p.strip() for p in drl.split(" . ") if p.strip()]:
                if "h" in part.lower() and any(c.isdigit() for c in part):
                    duration = part
                elif any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
                    rating = part
                else:
                    language = part

            # — expand the accordion
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(3)  # wait for the collapse to open

            # — now find *that* movie’s collapse panel
            collapse = summary.find_element(
                By.XPATH,
                "./following-sibling::div[contains(@class,'MuiCollapse-root')]"
            )
            details = collapse.find_element(By.CSS_SELECTOR, ".MuiAccordionDetails-root")

            # — pull every location card under this details
            show_details = []
            for loc_group in details.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-6z6qye"):
                # 1) location
                try:
                    loc = loc_group.find_element(
                        By.XPATH,
                        ".//figure[.//img[@alt='Pin icon']]/following-sibling::p"
                    ).text.strip()
                except:
                    loc = "Unknown"

                # 2) each cinema experience within this location
                experiences = []
                exp_cards = loc_group.find_elements(
                    By.XPATH,
                    ".//div[contains(@class,'MuiBox-root') and .//button[starts-with(@id,'session-')]]"
                )
                for card in exp_cards:
                    # — click Read More to get the cinema name
                    try:
                        read_more = card.find_element(By.CSS_SELECTOR, "a.css-scsw1e")
                        driver.execute_script("arguments[0].click()", read_more)
                        dialog = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                        cinema_name = dialog.find_element(By.TAG_NAME, "h4").text.strip()
                        # close dialog
                        dialog.find_element(By.XPATH, ".//button").click()
                        wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@role='dialog']")))
                    except:
                        cinema_name = "Unknown"

                    # — collect times
                    times = []
                    for btn in card.find_elements(By.XPATH, ".//button[starts-with(@id,'session-')]"):
                        txt = btn.find_element(By.TAG_NAME, "p").text.strip()
                        if txt:
                            times.append(txt)

                    experiences.append({"cinema": cinema_name, "times": times})

                show_details.append({
                    "location": loc,
                    "cinema":   experiences
                })

            # — collapse it back
            driver.execute_script("arguments[0].click()", summary)
            time.sleep(3)

            movies.append({
                "title":        title,
                "genres":       genres,
                "duration":     duration,
                "rating":       rating,
                "language":     language,
                "show_details": show_details
            })

        return movies

    finally:
        driver.quit()


if __name__ == "__main__":
    import pprint
    data = get_movies_with_showtimes("24 May")
    pprint.pprint(data)