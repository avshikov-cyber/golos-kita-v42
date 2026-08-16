# brain.py
# Брайан, который сам рисует по голосу

import os
import re
import random
import urllib.parse
import requests
import time  # <-- ДОБАВЛЕНО!

# Папка для сохранения результатов
SAVE_PATH = r"C:\Users\USER\OneDrive\Desktop\AI_images"
os.makedirs(SAVE_PATH, exist_ok=True)

# ==================== ГЕНЕРАТОР КАРТИНОК ====================
def generate_images(prompt):
    """Автоматически генерирует 4 картинки, сохраняет в папку"""
    model = "flux"
    enhanced_prompt = f"{prompt}, masterpiece, highly detailed, 4K, photorealistic, cinematic lighting"
    encoded = urllib.parse.quote(enhanced_prompt)
    base_url = f"https://image.pollinations.ai/prompt/{encoded}"

    used_seeds = set()
    saved_files = []

    for i in range(4):
        while True:
            seed = random.randint(1, 999999)
            if seed not in used_seeds:
                used_seeds.add(seed)
                break

        url = f"{base_url}?model={model}&width=1024&height=1024&seed={seed}&quality=high"
        filename = os.path.join(SAVE_PATH, f"brain_img_{int(time.time())}_{i+1}.png")

        try:
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(resp.content)
                saved_files.append(filename)
        except:
            pass

    return saved_files

# ==================== ДИСПЕТЧЕР ====================
def think(command_text):
    """Разбирает команду и запускает нужное действие"""
    cmd_lower = command_text.lower()

    # Если команда содержит "нарисуй", парсим промпт
    if "нарисуй" in cmd_lower:
        # Вырезаем промпт: убираем "брайан", "нарисуй" и остаётся суть
        prompt = re.sub(r'(брайан|brain|нарисуй)', '', command_text, flags=re.IGNORECASE).strip()
        if not prompt:
            return "Я не услышал, что именно нарисовать. Попробуй ещё раз."

        files = generate_images(prompt)
        if files:
            return f"Нарисовал {len(files)} картинок с {prompt}. Лежат в папке AI_images."
        else:
            return "Что-то пошло не так при рисовании."

    # Приветствие
    if "привет" in cmd_lower:
        return "Привет, капитан! Я тут подумал: а не нарисовать ли нам чего-нибудь?"

    return "Я не совсем понял, что ты хочешь."