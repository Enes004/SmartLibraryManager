import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

# Chrome seçeneklerini oluştur
chrome_options = Options()

# ChromeDriver'i başlat
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

# Web sitesine git
driver.get("https://kutuphane.uskudar.bel.tr/yordam/?p=2&dil=0&devam=2f796f7264616d2f3f703d372664696c3d30")

# Explicit Wait kullanarak sayfanın yüklenmesini bekle
wait = WebDriverWait(driver, 30)  # Bekleme süresini artırdık

# Şifre alanını bekle
sifre_input = wait.until(EC.presence_of_element_located((By.NAME, "aSifre")))

# TC Kimlik Numarası alanını bekle
tc_input = wait.until(EC.presence_of_element_located((By.NAME, "uyeKodKN")))

# Şifreyi ve TC kimlik numarasını gir
sifre_input.send_keys("şifreniyaz")  # Şifrenizi buraya yazın
tc_input.send_keys("tcni yaz")  # TC kimlik numaranızı buraya yazın

# Formu gönder
tc_input.send_keys(Keys.RETURN)

# CAPTCHA'yı çözmek için bekleme süresi ekleyelim (7 saniye)
try:
    captcha_wait = WebDriverWait(driver, 7)
    captcha_element = captcha_wait.until(EC.presence_of_element_located((By.ID, "g-recaptcha")))  # CAPTCHA öğesi
    print("Captcha yükleniyor...")
except Exception as e:
    print(f"Captcha yüklenirken bir hata oluştu: {e}")

# Tarih seçme dropdown'ını bul
tarih_dropdown = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tarihSec")))

# Dropdown menüsünden bir tarih seç (örneğin 18.01.2025)
tarih_select = Select(tarih_dropdown)
tarih_select.select_by_value("xx.xx.xxxx")  # Burada istediğin tarihi değiştirebilirsin

# Koltukların güncellenmesi için yenileme işlemini başlat
yenile_buton = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "sandalyeMusaitlikGetirBtn")))
yenile_buton.click()
print("Sandalyeler güncelleniyor...")

# Kısa bir bekleme (dropdown güncellenmesi için)
time.sleep(5)  # Bekleme süresini biraz daha uzun tuttuk

# Saat dropdown'ını bul
saat_dropdown = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "saatSec")))

# Saat seçeneklerini al
saat_options = saat_dropdown.find_elements(By.TAG_NAME, "option")

# Saatleri kontrol et ve uygun bir seçenek varsa seçim yap
bos_koltuk = 0
for option in saat_options:
    if "08:00 - 14:00" in option.text:
        try:
            bos_koltuk = int(option.text.split('[')[-1].split(']')[0])  # Boş koltuk sayısını al
            if bos_koltuk > 0:
                print(f"Boş koltuk bulundu: {bos_koltuk}")
                select = Select(saat_dropdown)
                select.select_by_value(option.get_attribute('value'))  # Doğru saat seçeneğini seçiyoruz
                break
        except Exception as e:
            print(f"Saat seçimi sırasında bir hata oluştu: {e}")

if bos_koltuk > 0:
    # "Benim İçin Sandalye Seç" butonuna tıkla
    sandalye_sec_buton = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "rastgele")))
    sandalye_sec_buton.click()

    # "Evet" butonuna tıkla
    evet_buton = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "evet")))
    evet_buton.click()
    print("Rezervasyon başarılı!")

    # Kapat butonuna tıklama ve sayfayı yenileme işlemi
    def close_modal(driver):
        try:
            # "Kapat" butonunu (✕) tıklamak için span elemanını bekle
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@aria-hidden='true' and contains(text(),'✕')]"))
            )
            close_button.click()  # Kapat butonuna tıklıyoruz
            print("Kapat butonuna tıklandı.")
            time.sleep(2)  # Butonun tıklanmasının ardından bekleme
            return True
        except Exception as e:
            print(f"Kapat butonu bulunamadı veya başka bir hata oluştu: {e}")
            return False  # Kapatma işlemi yapılmadı

    if close_modal(driver):
        driver.refresh()  # Sayfayı yenile
        time.sleep(2)  # Sayfanın yenilenmesini bekleyelim

    driver.quit()  # Tarayıcıyı kapat
else:
    print("Boş koltuk yok, tekrar kontrol ediliyor...")
