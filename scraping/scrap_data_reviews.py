from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

options = Options()
options.add_argument('--lang=id')
options.add_argument('accept-language=id-ID,id')
driver = webdriver.Chrome(options=options)

url = "https://www.google.com/maps/place/Kopi+Kenangan+-+Central+Park+2/@-6.1749796,106.7879275,17z/data=!3m1!5s0x2e69f65f3f899cb3:0x38fe444e117f084!4m8!3m7!1s0x2e69f7b749ee686f:0x4603ba74d2555193!8m2!3d-6.1749796!4d106.7905024!9m1!1b1!16s%2Fg%2F11h77lmkzc?entry=ttu&g_ep=EgoyMDI2MDUyMC4wIKXMDSoASAFQAw%3D%3D"
driver.get(url)
time.sleep(5)

try:
    driver.find_element(
        By.XPATH, "//span[contains(text(), 'Ulasan lainya') or contains(text(), 'More reviews')]/ancestor::button"
    ).click()
    time.sleep(3)
except:
    pass

reviews = []
seen = set()

last_review_count = 0
scroll_attempts = 0

print("Mulai mengekstrak ulasan, mohon tunggu proses scrolling...")

while True:
    # --- tombol 'See more' ---
    more_buttons = driver.find_elements(
        By.XPATH,
        "//button[@aria-label='See more' and @aria-expanded='false']"
    )
    for btn in more_buttons:
        try:
            driver.execute_script("arguments[0].click();", btn)
        except:
            pass
            
    # --- Tangkap elemen ulasan ---
    review_elements = driver.find_elements(By.CLASS_NAME, "jftiEf")
    
    # Pengaman jika ulasan belum muncul (mencegah index out of range)
    if len(review_elements) == 0:
        time.sleep(3)
        continue
    
    # --- Ekstrak teks ---
    for review_element in review_elements:
        try:
            nama_pengulas = review_element.find_element(By.CLASS_NAME, "d4r55").text.strip()
            try:
                ulasan = review_element.find_element(By.CLASS_NAME, "MyEned").text.strip()
            except:
                ulasan = ""
            try:
                rating = review_element.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
            except:
                rating = "Tidak ada rating"

            if (nama_pengulas, ulasan, rating) not in seen:
                reviews.append((nama_pengulas, ulasan, rating))
                seen.add((nama_pengulas, ulasan, rating))
        except Exception:
            continue
    
    print(f"\rUlasan terkumpul saat ini: {len(reviews)}", end="")

    # --- Proses Scrolling ---
    try:
        last_review = review_elements[-1]
        
        # [PERBAIKAN] JavaScript dengan teknik "Jiggle" (scroll naik dikit, lalu turun)
        driver.execute_script("""
            let el = arguments[0];
            let parent = el.parentElement;
            while (parent) {
                if (parent.scrollHeight > parent.clientHeight) {
                    // Pancing sensor Google: naikkan scroll sedikit, lalu turunkan mentok
                    parent.scrollTop = parent.scrollTop - 100; 
                    setTimeout(function() {
                        parent.scrollTop = parent.scrollHeight;
                    }, 500);
                    break; // Berhenti di container scroll pertama
                }
                parent = parent.parentElement;
            }
        """, last_review)
        time.sleep(4)
        
    except Exception as e:
        print(f"\nGagal melakukan scroll: {e}")
        break

    # --- Pengecekan Akhir (Mencegah berhenti terlalu dini) ---
    if len(reviews) == last_review_count:
        scroll_attempts += 1
        # [PERBAIKAN] Toleransi gagal scroll dinaikkan dari 3 jadi 5 (berjaga-jaga koneksi lambat)
        if scroll_attempts >= 5: 
            print("\nSudah mencapai akhir ulasan (mentok).")
            break
    else:
        scroll_attempts = 0
        last_review_count = len(reviews)

pd.DataFrame(reviews, columns=["Nama Pengulas", "Ulasan", "Rating"]).to_csv("KopiKenangan-CentralPark2.csv", index=False)
print(f"Selesai! Berhasil menyimpan {len(reviews)} ulasan ke KopiKenangan-CentralPark2.csv")
driver.quit()