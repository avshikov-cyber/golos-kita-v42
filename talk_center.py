import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import base64
import time
import threading
import traceback

# ==================== НАСТРОЙКИ ====================
PACKAGE = "com.stcodesapp.text2speech"

# Координаты для TECNO BG6
FIELD_TAP_X, FIELD_TAP_Y = 80, 410
SPEAK_TAP_X, SPEAK_TAP_Y = 625, 605


def speak_via_phone(text):
    try:
        # Кодируем текст в Base64
        text_b64 = base64.b64encode(text.encode('utf-8')).decode('ascii')

        # Вся цепочка команд одной строкой — как в CMD
        cmd = (
            'adb shell input keyevent 224 && '
            'timeout /t 2 /nobreak && '
            'adb shell input swipe 360 1400 360 400 300 && '
            'timeout /t 2 /nobreak && '
            f'adb shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1 && '
            'timeout /t 5 /nobreak && '
            f'adb shell input tap {FIELD_TAP_X} {FIELD_TAP_Y} && '
            'timeout /t 2 /nobreak && '
            f'adb shell am broadcast -a ADB_INPUT_B64 --es msg {text_b64} && '
            'timeout /t 2 /nobreak && '
            f'adb shell input tap {SPEAK_TAP_X} {SPEAK_TAP_Y}'
        )

        subprocess.run(cmd, shell=True, capture_output=True, timeout=60)

        return True, "Озвучено"
    except Exception as e:
        traceback.print_exc()
        return False, str(e)


class TalkCenter:
    def __init__(self, root):
        self.root = root
        self.root.title("🐋 ГОВОРЯЩИЙ ТЕЛЕФОН")
        self.root.geometry("700x550")
        self.root.configure(bg="#0B1A2E")

        tk.Label(root, text="🐋 ГОВОРЯЩИЙ ТЕЛЕФОН", font=("Segoe UI", 18, "bold"),
                 fg="#38BDF8", bg="#0B1A2E").pack(pady=10)

        text_frame = tk.LabelFrame(root, text="📝 ТЕКСТ ДЛЯ ОЗВУЧКИ",
                                   bg="#0B1A2E", fg="#FBBF24", font=("Segoe UI", 11, "bold"))
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.text_input = scrolledtext.ScrolledText(text_frame, height=8, font=("Segoe UI", 12),
                                                     bg="#1E2A3A", fg="#E0F2FE",
                                                     insertbackground="#E0F2FE", wrap=tk.WORD)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_input.insert("1.0", "Привет, капитан!")

        # Контекстное меню
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Копировать", command=lambda: self.text_input.event_generate("<<Copy>>"))
        self.menu.add_command(label="Вставить", command=lambda: self.text_input.event_generate("<<Paste>>"))
        self.menu.add_command(label="Вырезать", command=lambda: self.text_input.event_generate("<<Cut>>"))
        self.menu.add_separator()
        self.menu.add_command(label="Выделить всё", command=lambda: self.text_input.tag_add("sel", "1.0", "end"))
        self.text_input.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))
        self.text_input.bind("<Control-v>", lambda e: self.text_input.event_generate("<<Paste>>"))
        self.text_input.bind("<Control-V>", lambda e: self.text_input.event_generate("<<Paste>>"))

        btn_frame = tk.Frame(root, bg="#0B1A2E")
        btn_frame.pack(fill=tk.X, padx=15, pady=5)

        self.speak_btn = tk.Button(btn_frame, text="🔊 ОЗВУЧИТЬ", bg="#4ADE80", fg="black",
                                    font=("Segoe UI", 14, "bold"), command=self.speak)
        self.speak_btn.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(root, text="🟢 Готов", bg="#0B1A2E", fg="#4ADE80",
                                      font=("Segoe UI", 11))
        self.status_label.pack(pady=10)

    def speak(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите текст!")
            return

        self.status_label.config(text="🔄 Озвучиваю...", fg="#FBBF24")
        self.speak_btn.config(state=tk.DISABLED)
        self.root.update()

        def run():
            success, result = speak_via_phone(text)
            if success:
                self.status_label.config(text=f"✅ {result}", fg="#4ADE80")
            else:
                self.status_label.config(text=f"❌ {result}", fg="#F87171")
            self.speak_btn.config(state=tk.NORMAL)

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = TalkCenter(root)
    root.mainloop()