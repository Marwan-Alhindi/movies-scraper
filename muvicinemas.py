"""
✅ Selected Riyadh
✅ Clicked All Day
✅ Clicked Show Results
"""

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