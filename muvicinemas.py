"""
✅ Selected Riyadh
✅ Clicked All Day
✅ Clicked Show Results
"""


# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import time


# def get_movie_titles_for_date(day_text="23 May"):
#     options = Options()
#     # options.add_argument("--headless")  # Uncomment to run headless
#     options.add_argument("--window-size=1920,1080")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#     try:
#         driver.get("https://www.muvicinemas.com/en/movie-finder")
#         wait = WebDriverWait(driver, 15)

#         # Step 1: Select Riyadh
#         try:
#             riyadh_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Riyadh')]")))
#             riyadh_option.click()
#             time.sleep(1)

#             select_btn = driver.find_element(By.XPATH, "//button[contains(., 'Select')]")
#             select_btn.click()
#             print("✅ Selected Riyadh")
#             time.sleep(3)
#         except:
#             print("ℹ️ City selection not needed or already set")

#         # Step 2: Select the desired date
#         days = driver.find_elements(By.CSS_SELECTOR, '[class*="MuiToggleButton-root"]')
#         for day in days:
#             if day_text.lower() in day.text.lower():
#                 day.click()
#                 print(f"✅ Selected day: {day.text}")
#                 break
#         time.sleep(1)

#         # Step 3: Click "All Day"
#         all_day_divs = driver.find_elements(By.CSS_SELECTOR, 'div[class*="MuiBox-root"]')
#         for div in all_day_divs:
#             if "all day" in div.text.lower():
#                 driver.execute_script("arguments[0].click();", div)
#                 print("✅ Clicked All Day")
#                 break
#         time.sleep(1)

#         # Step 4: Click "Show Results"
#         show_results_btn = wait.until(EC.element_to_be_clickable((By.ID, "show-results-button")))
#         driver.execute_script("arguments[0].click();", show_results_btn)
#         print("✅ Clicked Show Results")
#         time.sleep(3)

#         # Step 5: Scroll the infinite-scroll container to load all movies
#         scroll_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.infinite-scroll-component')))
#         last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)

#         while True:
#             driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_container)
#             time.sleep(2)  # wait for new items to load
#             new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
#             if new_height == last_height:
#                 break
#             last_height = new_height

#         # Step 6: Extract all movie titles
#         movie_titles = set()
#         containers = scroll_container.find_elements(By.CSS_SELECTOR, 'h1[class*="MuiTypography-body1"]')

#         for title_element in containers:
#             title = title_element.text.strip()
#             if title:
#                 movie_titles.add(title)

#         return list(movie_titles)

#     finally:
#         driver.quit()


# # Example usage
# if __name__ == "__main__":
#     day = "23 May"
#     movies = get_movie_titles_for_date(day)
#     print(f"\n🎬 Movies in Riyadh on {day}:")
#     for i, m in enumerate(movies, 1):
#         print(f"{i}. {m}")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_movie_titles_for_date(day_text="23 May"):
    options = Options()
    # options.add_argument("--headless")  # uncomment for headless
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://www.muvicinemas.com/en/movie-finder")

        # 1) City select
        try:
            riyadh = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[.='Riyadh']")))
            riyadh.click()
            driver.find_element(By.XPATH, "//button[.='Select']").click()
            print("✅ Selected Riyadh")
            time.sleep(2)
        except:
            print("ℹ️ City popup skipped")

        # 2) Pick date
        for btn in driver.find_elements(By.CSS_SELECTOR, '[class*="MuiToggleButton-root"]'):
            if day_text.lower() in btn.text.lower():
                btn.click()
                print(f"✅ Selected day: {btn.text}")
                break
        time.sleep(1)

        # 3) Click “All Day”
        for div in driver.find_elements(By.CSS_SELECTOR, 'div[class*="MuiBox-root"]'):
            if "all day" in div.text.lower():
                driver.execute_script("arguments[0].click()", div)
                print("✅ Clicked All Day")
                break
        time.sleep(1)

        # 4) “Show Results”
        show = wait.until(EC.element_to_be_clickable((By.ID, "show-results-button")))
        driver.execute_script("arguments[0].click()", show)
        print("✅ Clicked Show Results")
        time.sleep(2)

        # 5) Scroll the _window_ until no more new content
        last_h = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # give new items time to load
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

        # 6) Grab every movie title <h1> inside the infinite‐scroll container
        titles = driver.find_elements(
            By.CSS_SELECTOR,
            "div.infinite-scroll-component h1.MuiTypography-body1"
        )
        movies = [t.text.strip() for t in titles if t.text.strip()]

        return movies

    finally:
        driver.quit()


if __name__ == "__main__":
    day = "23 May"
    all_movies = get_movie_titles_for_date(day)
    print(f"\n🎬 Movies in Riyadh on {day} ({len(all_movies)} total):")
    for i, movie in enumerate(all_movies, 1):
        print(f"{i}. {movie}")