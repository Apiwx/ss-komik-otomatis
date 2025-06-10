from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageStat
import os, requests, time

# --- Konfigurasi URL ---
url = 'https://asuracomic.net/series/nano-machine-72ffa015/chapter/1'

# --- Proses parsing URL jadi nama folder ---
parts = url.strip("/").split("/")
chapter_name = parts[-1].replace("-", " ").title()
manhwa_slug = parts[4].replace("-", " ").title()

# --- Folder utama ---
base_folder = r"C:\ss manhwa"
chapter_path = os.path.join(base_folder, manhwa_slug, chapter_name)
os.makedirs(chapter_path, exist_ok=True)

# --- Jalankan browser dan ambil gambar ---
driver = webdriver.Chrome()
driver.get(url)
print("❗ Silakan scroll dulu di browser sampai semua gambar muncul...")
input("✅ Tekan ENTER setelah selesai scroll...")

imgs = driver.find_elements(By.TAG_NAME, "img")
n = 1
for img in imgs:
    src = img.get_attribute("src")
    if src and "gg.asuracomic.net/storage/media/" in src:
        try:
            ext = src.split('.')[-1].split('?')[0]
            img_data = requests.get(src).content
            with open(os.path.join(chapter_path, f"panel_{n}.{ext}"), 'wb') as f:
                f.write(img_data)
            print(f"✅ panel_{n}.{ext}")
            n += 1
        except:
            print(f"❌ gagal simpan gambar")
driver.quit()
print(f"\n🎉 Gambar disimpan ke: {chapter_path}")

# --- Konversi dan pemotongan gambar ---
converted_path = os.path.join(chapter_path, "jpg_converted")
output_path = os.path.join(chapter_path, "scene_split")
os.makedirs(converted_path, exist_ok=True)
os.makedirs(output_path, exist_ok=True)

print(f"\n🔁 Mengonversi + memotong folder: {chapter_name}")

FLAT_VARIANCE_THRESHOLD = 2
MIN_EMPTY_HEIGHT = 20

def is_empty_line(crop):
    stat = ImageStat.Stat(crop)
    return max(stat.stddev) < FLAT_VARIANCE_THRESHOLD

# Convert .webp ke .jpg
for file in os.listdir(chapter_path):
    if file.lower().endswith(".webp"):
        try:
            img = Image.open(os.path.join(chapter_path, file)).convert("RGB")
            jpg_name = os.path.splitext(file)[0] + ".jpg"
            img.save(os.path.join(converted_path, jpg_name), "JPEG")
            print(f"🟢 dikonversi: {jpg_name}")
        except Exception as e:
            print(f"❌ gagal konversi {file}: {e}")

# Potong scene dari JPG
for file in os.listdir(converted_path):
    if file.lower().endswith(".jpg"):
        img_path = os.path.join(converted_path, file)
        img = Image.open(img_path)
        width, height = img.size

        cuts = []
        y = 0
        start_y = 0

        while y < height:
            empty_height = 0
            while y < height:
                line_crop = img.crop((0, y, width, y + 1))
                if is_empty_line(line_crop):
                    empty_height += 1
                    y += 1
                else:
                    break
            if empty_height >= MIN_EMPTY_HEIGHT:
                end_y = y - empty_height
                if end_y > start_y:
                    cuts.append((start_y, end_y))
                start_y = y
            y += 1
        if start_y < height:
            cuts.append((start_y, height))

        for i, (y1, y2) in enumerate(cuts, 1):
            scene_crop = img.crop((0, y1, width, y2))
            scene_name = f"{os.path.splitext(file)[0]}_scene_{i}.jpg"
            scene_crop.save(os.path.join(output_path, scene_name))
            print(f"✅ dipotong: {scene_name}")
