import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROFILE_DIR = "./user_data"
SEARCH_URL = "https://id.jobstreet.com/id/jobs?daterange=1&tags=new"

def is_logged_in(driver):
    driver.get("https://www.jobstreet.co.id")
    time.sleep(3)
    return "Masuk" not in driver.page_source

def manual_login(driver):
    print("🔑 Silakan login manual...")
    driver.get("https://www.jobstreet.co.id")
    input("✅ Tekan ENTER setelah login dan sampai dashboard...")

def get_job_links_from_page(driver):
    jobs = driver.find_elements(By.XPATH, "//article")
    urls = []
    for job in jobs:
        try:
            job.find_element(By.XPATH, ".//*[contains(text(), 'menit yang lalu')]")
            link = job.find_element(By.XPATH, ".//a[contains(@href, '/id/job/')]")
            href = link.get_attribute("href")
            full_url = f"https://id.jobstreet.com{href}" if href.startswith("/id/job/") else href
            urls.append(full_url)
        except NoSuchElementException:
            continue
    return urls

def safe_click_button(driver, button_text, timeout=10):
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(.,'{button_text}')]/ancestor::span[@role='button' or @class]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
        time.sleep(0.5)
        button.click()
        return True
    except Exception as e:
        print(f"⚠️ Gagal klik tombol '{button_text}': {e}")
        return False

def apply_to_job(driver, job_url):
    driver.execute_script(f"window.open('{job_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)
    print(f"🔅 Melamar ke: {job_url}")

    if not safe_click_button(driver, "Lamaran Cepat"):
        print("❌ Tombol Lamaran Cepat tidak ditemukan.")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return

    time.sleep(2)
    for idx in range(1, 4):  # Klik Lanjut 3x
        if not safe_click_button(driver, "Lanjut"):
            print(f"⚠️ Gagal klik Lanjut #{idx}, kemungkinan ada field wajib.")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return
        time.sleep(2)

    if not safe_click_button(driver, "Kirim lamaran"):
        print("❌ Gagal klik Kirim lamaran.")
    else:
        print("✅ Lamaran berhasil dikirim!")

    time.sleep(4)  # Tambahan delay agar tombol benar-benar terkirim
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def main():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    driver = uc.Chrome(options=options)

    if not is_logged_in(driver):
        manual_login(driver)

    page_num = 1
    while True:
        print(f"📄 Halaman {page_num}: Mencari pekerjaan...")
        driver.get(f"{SEARCH_URL}&page={page_num}")
        time.sleep(5)

        job_links = get_job_links_from_page(driver)
        if not job_links:
            print("❌ Tidak ditemukan pekerjaan pada halaman ini.")
            break

        for url in job_links:
            apply_to_job(driver, url)
            time.sleep(3)

        page_num += 1  # Otomatis lanjut ke halaman berikutnya

    print("👋 Program selesai. Menutup browser...")
    driver.quit()

if __name__ == "__main__":
    main()
