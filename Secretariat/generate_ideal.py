import requests
import urllib.parse
import os
import time
import random

# ==================== ПУТЬ СОХРАНЕНИЯ ====================
SAVE_PATH = r"C:\Users\USER\OneDrive\Desktop\AI_images"
os.makedirs(SAVE_PATH, exist_ok=True)

# ==================== МОДЕЛИ ====================
MODELS = {
    "flux": "Универсальная",
    "flux-realism": "Фотореализм",
    "zimage": "Четкая структура",
    "gptimage": "Максимум качества",
    "ideogram-v4-turbo": "Для текста",
}

# ==================== ТЕГИ ДЛЯ РАЗНООБРАЗИЯ ====================
LIGHTING = [
    "cinematic lighting",
    "soft lighting",
    "dramatic lighting",
    "golden hour lighting"
]

COMPOSITION = [
    "rule of thirds",
    "center composition",
    "symmetrical composition",
    "dynamic angle"
]

DETAIL = [
    "hyper realistic",
    "extreme detail",
    "ultra sharp",
    "skin texture visible"
]

CAMERA = [
    "85mm lens",
    "cinematic shot",
    "wide angle",
    "macro photography"
]

QUALITY_TAGS = [
    "masterpiece",
    "highly detailed",
    "4K resolution",
    "photorealistic",
    "cinematic lighting",
    "sharp focus",
    "crisp details",
    "ultra-detailed",
    "high contrast",
    "micro details visible"
]

NEGATIVE = [
    "blurry",
    "low quality",
    "bad anatomy",
    "distorted",
    "extra fingers"
]

# ==================== ПЕРЕВОД НА АНГЛИЙСКИЙ ====================
def translate_to_english(text):
    """
    Переводит промпт с русского на английский.
    Если перевод не удался, возвращает исходный текст.
    """
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "en",
            "dt": "t",
            "q": text
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and data[0] and data[0][0] and data[0][0][0]:
                return data[0][0][0]
    except Exception as e:
        print(f"⚠️ Ошибка перевода: {e}")
    return text

# ==================== АВТОМАТИЧЕСКИЙ ВЫБОР МОДЕЛИ ====================
def auto_model(prompt):
    p = prompt.lower()
    if "текст" in p:
        return "ideogram-v4-turbo"
    if "фото" in p or "реал" in p:
        return "flux-realism"
    return "flux"

# ==================== УЛУЧШЕНИЕ ПРОМПТА ====================
def enhance_prompt(prompt):
    """Случайным образом добавляет в промпт теги для разнообразия"""
    enhanced = prompt.strip()

    # Добавляем случайные элементы
    enhanced += ", " + random.choice(CAMERA)
    enhanced += ", " + random.choice(DETAIL)
    enhanced += ", " + random.choice(LIGHTING)
    enhanced += ", " + random.choice(COMPOSITION)

    # Добавляем стандартные теги качества
    enhanced += ", " + ", ".join(QUALITY_TAGS)

    # Добавляем негативный промпт
    enhanced += ", --no " + ", ".join(NEGATIVE)

    return enhanced

# ==================== ГЕНЕРАЦИЯ ====================
def generate(prompt, count=4):
    # 1. Переводим промпт
    print("\n🔄 Перевожу промпт...")
    prompt_en = translate_to_english(prompt)
    print(f"📝 Перевод: {prompt_en}")

    # 2. Выбираем модель
    model = auto_model(prompt_en)

    # 3. Улучшаем промпт
    enhanced = enhance_prompt(prompt_en)
    encoded = urllib.parse.quote(enhanced)

    base_url = f"https://image.pollinations.ai/prompt/{encoded}"

    print(f"\n🧠 Модель: {model}")
    print(f"✨ Промпт: {enhanced}")
    print(f"📁 Папка: {SAVE_PATH}")

    used_seeds = set()
    saved_files = []

    for i in range(count):
        # Генерируем уникальный seed
        while True:
            seed = random.randint(1, 999999)
            if seed not in used_seeds:
                used_seeds.add(seed)
                break

        url = (
            f"{base_url}"
            f"?model={model}&width=1024&height=1024"
            f"&seed={seed}&quality=high"
        )

        filename = os.path.join(
            SAVE_PATH,
            f"img_{int(time.time())}_{i+1}.png"
        )

        print(f"\n[{i+1}/{count}] Генерация (seed {seed})...")

        try:
            start_time = time.time()
            response = requests.get(url, timeout=120)

            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                saved_files.append(filename)
                print(f"✅ Сохранено: {filename}")
            else:
                print(f"❌ Ошибка: {response.status_code}")

            print(f"⏱️ {round(time.time() - start_time, 2)} сек")

        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

        time.sleep(1)

    print(f"\n✅ Сохранено {len(saved_files)} изображений в папке {SAVE_PATH}")
    return saved_files

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    print("\n🐋 ИДЕАЛЬНЫЙ ГЕНЕРАТОР КАРТИНОК")
    print("=" * 50)
    print("🔥 Автоматический перевод с русского")
    print("🔥 Умный выбор модели")
    print("🔥 Случайные теги для разнообразия")
    print("🔥 Гарантированно разные картинки")
    print("=" * 50)

    prompt = input("\n📝 Введите промпт (можно на русском): ")

    count = input("🎯 Сколько вариантов (по умолчанию 4): ")
    count = int(count) if count.strip().isdigit() else 4

    generate(prompt, count)

    print(f"\n🚀 Готово! Все файлы сохранены в папке: {SAVE_PATH}")