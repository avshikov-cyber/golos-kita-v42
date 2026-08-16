import os
import json
import time
import webbrowser
import datetime
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3
import pyautogui
import pygetwindow as gw
import subprocess
import re
import keyboard
import sys
import requests
import ctypes

sys.path.append(r"C:\Users\USER\OneDrive\Desktop\voice_blocks")
import clipboard_control as cb
import window_control as wc
import media_control as mc

MODEL_PATH = r"C:\vosk-model-ru-0.42"
SAMPLE_RATE = 16000
WAKE_WORD = "голос"
SLEEP_AFTER_INACTIVITY = 15

PLAY_BUTTON_X = 1102
PLAY_BUTTON_Y = 656
LIKE_BUTTON_X = 1304
LIKE_BUTTON_Y = 572
DISLIKE_BUTTON_X = 900
DISLIKE_BUTTON_Y = 572
POINT_BUTTON_X = 98
POINT_BUTTON_Y = 280
CINEMA_BUTTON_X = 1100
CINEMA_BUTTON_Y = 874
LINK_BUTTON_X = 1497
LINK_BUTTON_Y = 829
YOUTUBE_BUTTON_X = 967
YOUTUBE_BUTTON_Y = 90
MINIMIZE_BUTTON_X = 1599
MINIMIZE_BUTTON_Y = 871

FIELD_BUTTON_X = 1110
FIELD_BUTTON_Y = 700

COMMANDS = {
    "включи музыку": ["включи музыку", "включить музыку", "включи музку", "включить музку", "включи музика", "вруби музыку", "запусти музыку"],
    "открой музыку": ["открой музыку", "открыть музыку", "открой музку", "открой музику"],
    "яндекс музыка": ["яндекс музыка", "яндекс музка", "яндекс музика", "яндекс музык"],
    "закрой музыку": ["закрой музыку", "закрыть музыку", "закрой музку", "закрой музику", "выключи музыку", "выключить музыку"],
    "музыка": ["музыка", "музыку", "музка", "музика", "музык", "мужик"],
    "пауза": ["пауза", "паузу", "паза", "пауз", "ауза", "поставь на паузу", "поставить на паузу"],
    "громче": ["громче", "громко", "громка", "громше", "громкой", "погромче", "сделай громче", "увеличь громкость"],
    "тише": ["тише", "тихо", "тиха", "тихой", "потише", "сделай тише", "уменьши громкость"],
    "дальше": ["дальше", "следующий", "следующая", "следующее", "вперед", "переключи", "следующий трек"],
    "назад": ["назад", "предыдущий", "предыдущая", "предыдущее", "назад трек"],
    "лайк": ["лайк", "нравится", "нравитца", "лайкни", "лайка", "лайкнуть", "поставь лайк", "мне нравится"],
    "дизлайк": ["дизлайк", "дизлайкни", "плохо", "не нравится", "не нравитца"],
    "точка": ["точка", "точку"],
    "поле": ["поле", "полю"],
    "язык": ["язык", "раскладка"],
    "тык": ["тык", "дык", "ик"],
    "поиск": ["поиск", "найти"],
    "таб": ["таб", "саб", "тап", "таб", "переключи окно", "смени окно", "переключиться"],
    "вкладка": ["вкладка", "вкладки", "вклатка", "кладка", "вкладку", "вкладке", "переключи вкладку", "смени вкладку"],
    "время": ["время", "време", "времени", "времечко", "сколько времени", "который час", "часы"],
    "погода": ["погода", "погоду", "прогноз", "погодка"],
    "браузер": ["браузер", "брауза", "браузор", "гугл", "гугле", "открой браузер", "запусти браузер", "интернет", "хром"],
    "закрой браузер": ["закрой браузер", "закрыть браузер", "закрой гугл", "закрой хром", "закрыть хром"],
    "свернуть окна": ["свернуть все окна", "сверни все окна", "свернуть окна", "окна", "сверни окна", "свернуть всё"],
    "скопировать": ["скопировать", "скопируй", "копировать", "копай"],
    "вставить": ["вставить", "вставь", "паст"],
    "вырезать": ["вырезать", "вырежь"],
    "закрыть окно": ["закрыть окно", "закрой окно", "закрой", "закрыть"],
    "развернуть окно": ["развернуть окно", "разверни окно", "развернуть", "разверни"],
    "свернуть окно": ["свернуть окно", "сверни окно", "свернуть"],
    "переключить окно": ["другой", "другое", "новый", "следующее окно", "переключи окно"],
    "выключи компьютер": ["выключи компьютер", "выключить компьютер", "выключи пк", "выключить пк", "выруби компьютер", "выруби пк"],
    "голос спать": ["голос спать", "голос, спать", "голос засни", "голос усни", "голос уйди", "спать", "сон", "усни"],
    "стоп": ["стоп", "хватит", "до свидания", "выключись", "замолчи", "перестань"],
    "кино": ["кино", "ино", "и но"],
    "ссылка": ["ссылка", "ссылку", "сылка"],
    "ютюб": ["ютюб", "ютуб", "ютьюб", "ютубе"],
    "нарисуй": ["нарисуй", "рисуй"],
}

def speak(text: str):
    print(f"🤖 {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 168)
        engine.setProperty("volume", 0.92)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"TTS ошибка: {e}")

def get_weather(city="Ульяновск"):
    try:
        url = f"https://wttr.in/{city}?format=%t+%w+%c"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            weather_text = response.text.strip()
            parts = weather_text.split()
            temp = parts[0] if parts else "неизвестно"
            wind = parts[1] if len(parts) > 1 else "неизвестно"
            condition = " ".join(parts[2:]) if len(parts) > 2 else "ясно"
            return f"В {city} сейчас {condition}, температура {temp}, ветер {wind}"
        else:
            return f"Не удалось получить погоду для {city}. Попробуй позже."
    except Exception as e:
        return f"Ошибка при запросе погоды: {e}"

def minimize_all_windows():
    pyautogui.click(MINIMIZE_BUTTON_X, MINIMIZE_BUTTON_Y)
    time.sleep(0.5)

def click_play():
    pyautogui.click(PLAY_BUTTON_X, PLAY_BUTTON_Y)
    print("🎵 Клик по кнопке Play")

def click_like():
    pyautogui.click(LIKE_BUTTON_X, LIKE_BUTTON_Y)
    print("❤️ Клик по кнопке Лайк")

def click_dislike():
    focus_window("Яндекс Музыка")
    pyautogui.click(DISLIKE_BUTTON_X, DISLIKE_BUTTON_Y)
    print("👎 Клик по кнопке Дизлайк")

def click_point():
    pyautogui.press('enter')
    print("📍 Точка — отправка Enter")
    speak("Ага, отправил")

def click_field():
    pyautogui.click(FIELD_BUTTON_X, FIELD_BUTTON_Y)
    print(f"📍 Поле — клик по координатам ({FIELD_BUTTON_X}, {FIELD_BUTTON_Y})")
    speak("Ага, поле")

def click_cinema():
    pyautogui.click(CINEMA_BUTTON_X, CINEMA_BUTTON_Y)
    print("🎬 Клик по кнопке Кино")

def click_link():
    pyautogui.click(LINK_BUTTON_X, LINK_BUTTON_Y)
    print("🔗 Клик по кнопке Ссылка")

def click_youtube():
    pyautogui.click(YOUTUBE_BUTTON_X, YOUTUBE_BUTTON_Y)
    print("▶️ Клик по кнопке Ютюб")

def focus_window(title_part):
    try:
        windows = gw.getWindowsWithTitle(title_part)
        if windows:
            win = windows[0]
            if not win.isActive:
                win.activate()
                time.sleep(0.5)
                print(f"✅ Фокус на окно: {win.title}")
                return True
            else:
                print(f"✅ Окно уже активно: {win.title}")
                return True
    except Exception as e:
        print(f"⚠️ Ошибка фокуса: {e}")
    return False

def focus_browser():
    try:
        browsers = ["Google Chrome", "Mozilla Firefox", "Microsoft Edge", "Яндекс Браузер"]
        for name in browsers:
            windows = gw.getWindowsWithTitle(name)
            if windows:
                win = windows[0]
                if not win.isActive:
                    win.activate()
                    time.sleep(0.3)
                    print(f"✅ Фокус на браузер: {win.title}")
                    return True
                else:
                    print(f"✅ Браузер уже активен: {win.title}")
                    return True
    except Exception as e:
        print(f"⚠️ Ошибка фокуса на браузер: {e}")
    return False

def open_music_app():
    speak("Йеп, Открываю Яндекс Музыку")
    minimize_all_windows()
    time.sleep(0.5)
    app_path = r"C:\Users\USER\AppData\Local\Programs\YandexMusic\Яндекс Музыка.exe"
    if not os.path.exists(app_path):
        speak("Приложение Яндекс Музыка не найдено")
        print(f"❌ Файл не найден: {app_path}")
        return False
    try:
        subprocess.Popen([app_path], shell=True)
        print("✅ Приложение запущено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        speak("Не удалось запустить Яндекс Музыку")
        return False
    print("⏳ Ждём загрузки приложения (10 секунд)...")
    time.sleep(10)
    if focus_window("Яндекс Музыка"):
        print("✅ Приложение готово")
        return True
    else:
        print("⚠️ Не удалось найти окно Яндекс.Музыки")
        return False

def close_music_app():
    speak("Йеп, Закрываю Яндекс Музыку")
    try:
        result = os.popen('tasklist | findstr -i "Яндекс Музыка"').read()
        if "Яндекс Музыка" in result:
            os.system("taskkill /f /im \"Яндекс Музыка.exe\" 2>nul")
            print("✅ Приложение Яндекс.Музыки закрыто")
        else:
            windows = gw.getWindowsWithTitle("Яндекс Музыка")
            if windows:
                windows[0].close()
                print("✅ Окно Яндекс.Музыки закрыто")
            else:
                speak("Приложение Яндекс Музыка не найдено")
    except Exception as e:
        print(f"⚠️ Ошибка при закрытии: {e}")
        speak("Не удалось закрыть Яндекс Музыку")

def set_russian_layout():
    try:
        user32 = ctypes.windll.user32
        layouts_count = user32.GetKeyboardLayoutList(0, None)
        if layouts_count:
            layouts = (ctypes.c_ulong * layouts_count)()
            user32.GetKeyboardLayoutList(layouts_count, layouts)
            for layout in layouts:
                if layout & 0xFFFF == 0x0419:
                    user32.ActivateKeyboardLayout(layout, 0)
                    time.sleep(0.3)
                    print("🔤 Переключено на русскую раскладку (Windows API)")
                    return True
        print("⚠️ Русская раскладка не найдена, пробую Alt+Shift")
        keyboard.press('alt')
        time.sleep(0.05)
        keyboard.press('shift')
        time.sleep(0.05)
        keyboard.release('shift')
        keyboard.release('alt')
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"❌ Ошибка переключения раскладки: {e}")
        return False

def get_command(text: str):
    text = text.lower().strip()
    for key, variants in COMMANDS.items():
        for variant in variants:
            if variant in text:
                return key
    return None

def process_command(text: str):
    text = text.lower().strip()

    cmd = get_command(text)
    if not cmd:
        return None

    print(f"📌 Команда: {text}")

    if cmd == "стоп":
        speak("До свидания")
        return "exit"

    if cmd == "голос спать":
        speak("Ага, засыпаю")
        return "sleep"

    if cmd == "нарисуй":
        speak("Рисую...")
        try:
            import brain
            prompt = re.sub(r'(нарисуй|рисуй)', '', text, flags=re.IGNORECASE).strip()
            if not prompt:
                speak("Я не услышал, что именно нарисовать.")
                return None
            result = brain.think(f"нарисуй {prompt}")
            speak(result)
        except ImportError:
            speak("Брайан не найден. Проверь brain.py.")
        except Exception as e:
            speak(f"Ошибка: {e}")
        return None

    if cmd == "точка":
        click_point()
        return None

    if cmd == "поле":
        click_field()
        return None

    if cmd == "язык":
        keyboard.press_and_release('alt+shift')
        speak("Ага, переключил")
        return None

    if cmd == "тык":
        keyboard.press_and_release('tab')
        speak("Ага, тык")
        return None

    if cmd == "поиск":
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.3)
        pyautogui.hotkey('shift', 'tab')
        speak("Ага, поиск")
        return None

    if cmd == "переключить окно":
        keyboard.press('alt')
        time.sleep(0.05)
        keyboard.press('tab')
        time.sleep(0.05)
        keyboard.release('tab')
        keyboard.release('alt')
        time.sleep(0.2)
        speak("Ага, переключил")
        return None

    if cmd == "таб":
        pyautogui.hotkey('alt', 'tab')
        speak("Ага, переключил")
        return None

    if cmd == "вкладка":
        number_words = {"один":"1","два":"2","три":"3","четыре":"4","пять":"5","шесть":"6","семь":"7","восемь":"8","девять":"9","ноль":"0"}
        found = False
        for word, digit in number_words.items():
            if word in text:
                num = int(digit)
                if 1 <= num <= 9:
                    pyautogui.hotkey('ctrl', str(num))
                    speak(f"Ага, переключил на вкладку {num}")
                    found = True
                break
        if not found:
            pyautogui.hotkey('ctrl', 'tab')
            speak("Йеп, следующая вкладка")
        return None

    if cmd == "свернуть окна":
        minimize_all_windows()
        speak("Ага, свернул")
        return None

    if cmd == "громче":
        for _ in range(5):
            keyboard.press_and_release('volume up')
            time.sleep(0.05)
        speak("Ага, громче")
        return None
    if cmd == "тише":
        for _ in range(5):
            keyboard.press_and_release('volume down')
            time.sleep(0.05)
        speak("Ага, тише")
        return None

    if cmd == "скопировать":
        cb.copy_text()
        speak("Ага, скопировал")
        return None
    if cmd == "вставить":
        cb.paste_text()
        speak("Ага, вставил")
        return None
    if cmd == "вырезать":
        cb.cut_text()
        speak("Ага, вырезал")
        return None

    if cmd == "закрыть окно":
        wc.close_active_window()
        speak("Ага, закрыл")
        return None
    if cmd == "развернуть окно":
        wc.maximize_active_window()
        speak("Ага, развернул")
        return None
    if cmd == "свернуть окно":
        wc.minimize_active_window()
        speak("Ага, свернул")
        return None

    if cmd == "кино":
        click_cinema()
        speak("Ага, кино")
        return None
    if cmd == "ссылка":
        click_link()
        speak("Ага, ссылка")
        return None
    if cmd == "ютюб":
        click_youtube()
        speak("Ага, ютюб")
        return None

    if cmd == "браузер":
        minimize_all_windows()
        speak("Ага, Открываю браузер")
        webbrowser.open("https://google.com")
        return None
    if cmd == "закрой браузер":
        speak("Ага, Закрываю браузер")
        os.system("taskkill /im chrome.exe /f")
        return None

    if cmd == "закрой музыку":
        close_music_app()
        return None
    if cmd in ["включи музыку", "открой музыку", "яндекс музыка"]:
        open_music_app()
        return None
    if cmd == "музыка":
        if focus_window("Яндекс Музыка"):
            speak("Ага, Включаю музыку")
            click_play()
        else:
            speak("Йеп, сначала открой Яндекс Музыку")
        return None

    if cmd == "пауза":
        if not focus_window("Яндекс Музыка"):
            focus_browser()
        click_play()
        speak("Ага, Пауза")
        return None

    if cmd == "дальше":
        pyautogui.press('nexttrack')
        speak("Йеп, Следующий трек")
        return None
    if cmd == "назад":
        pyautogui.press('prevtrack')
        speak("Ага, Предыдущий трек")
        return None

    if cmd == "лайк":
        click_like()
        speak("Ага, лайк")
        return None
    if cmd == "дизлайк":
        click_dislike()
        speak("Ага, дизлайк")
        return None

    if cmd == "время":
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Ага, Сейчас {now}")
        return None

    if cmd == "погода":
        city = "Ульяновск"
        city_match = re.search(r'погода\s+в\s+([а-яА-ЯёЁ\s\-]+)', text)
        if city_match:
            city = city_match.group(1).strip()
        weather_report = get_weather(city)
        speak(weather_report)
        return None

    if cmd == "выключи компьютер":
        speak("Йеп, Вы уверены? Скажите 'да', чтобы выключить компьютер.")
        return "confirm_shutdown"

    return None

def main():
    print("🎤 Голосовой ассистент запущен. Скажите 'голос' для активации.")

    p = pyaudio.PyAudio()
    print("\n🎤 Доступные аудиоустройства (вход):")
    default_mic_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"   {i}: {info['name']}")
            if default_mic_index is None:
                default_mic_index = i
    input_device_index = default_mic_index
    print(f"\n🔊 Использую устройство ввода: {input_device_index}")

    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True, input_device_index=input_device_index, frames_per_buffer=8000)
    except Exception as e:
        print(f"❌ Ошибка открытия аудио: {e}")
        print("💡 Попробуй выбрать другое устройство или проверь микрофон.")
        return

    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    stream.start_stream()

    print("\n✅ Голос готов к работе. Скажите \"голос\" для активации.")

    active = False
    last_activity = time.time()
    shutdown_confirm = False

    try:
        while True:
            data = stream.read(8000, exception_on_overflow=False)

            if active and time.time() - last_activity > SLEEP_AFTER_INACTIVITY:
                speak("Йеп, засыпаю")
                active = False
                continue

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip().lower()
                if not text or len(text) < 3:
                    continue
                if not active:
                    if WAKE_WORD in text:
                        active = True
                        last_activity = time.time()
                        speak("Йеп, Слушаю, Хозяин")
                    continue
                response = process_command(text)
                if response == "exit":
                    break
                elif response == "sleep":
                    active = False
                    continue
                elif response == "confirm_shutdown":
                    shutdown_confirm = True
                    continue
                if shutdown_confirm:
                    if text.strip() == "да" or text.strip() == "выключай":
                        speak("Йеп, Выключаю компьютер")
                        os.system("shutdown /s /t 3")
                        break
                    else:
                        speak("Йеп, Отмена")
                        shutdown_confirm = False
                        active = False
                    continue
                last_activity = time.time()
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip().lower()

                if partial_text in ["тык", "дык", "ик"]:
                    keyboard.press_and_release('tab')
                    print("📍 Быстрый тык (partial)")
                    continue

                if not active and WAKE_WORD in partial_text:
                    active = True
                    last_activity = time.time()
                    speak("Йеп, Слушаю, Хозяин")
    except KeyboardInterrupt:
        speak("Йеп, Ассистент остановлен")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()