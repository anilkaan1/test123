import atexit
import base64
import os
import queue
import shutil
import sys
import tempfile
import threading
import time
import random
from multiprocessing import freeze_support, Process
from python_imagesearch.imagesearch import imagesearch, imagesearcharea
import pyautogui
from multiprocessing import Process, Queue
import cv2
from PIL import ImageGrab,Image
import numpy
import tkinter as tk
from tkinter import ttk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Change this path if your PNG assets are stored in a different directory.
IMAGE_BASE_PATH = SCRIPT_DIR


def image_path(*relative_parts):
    """Build an absolute path to an image by joining it with the base path."""
    return os.path.join(IMAGE_BASE_PATH, *relative_parts)

#can aalınca beklemiyor
#scroll map
#move the mouse an empty point
#bazen çıkışı basmasın
#dövüş bitti hatası

#key spammer duruma göre üst alt düz vurmalı
#ilk tur kombo

def process_log_queue(log_queue, text_widget):
    try:
        while True:
            message = log_queue.get_nowait()
            text_widget.configure(state='normal')
            text_widget.insert('end', message)
            text_widget.see('end')
            text_widget.configure(state='disabled')
    except queue.Empty:
        pass

    # Schedule the next log processing call
    root.after(100, process_log_queue, log_queue, text_widget)

class TextRedirector(object):
    def __init__(self, widget, log_queue):
        self.widget = widget
        self.log_queue = log_queue

    def write(self, str):
        self.log_queue.put(str)

    def flush(self):
        pass

class ThreadControl:
    def __init__(self, tab, log_text, target, status_text="Bot başlamadı"):
        self.tab = tab
        self.log_text = log_text
        self.target = target
        self.stop_thread = threading.Event()
        self.updating_time = False
        self.remaining_time = 0  # Kalan süreyi takip etmek için bir değişken ekleyelim
        self.kesilen_yaratik_count = 0  # Kesilen yaratık sayısını takip etmek için bir değişken

        self.temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)  # temp klasörünü oluştur

        # 2️⃣ Program kapanırken temp klasörünü sil
        atexit.register(self.temizle_temp_klasoru)  # Uygulama kapanırken temp klasörünü sil

        config_frame = tk.Frame(tab, background="#e6f7ff")
        config_frame.pack(pady=10,padx=15, side=tk.TOP)

        kayit_frame = tk.Frame(config_frame, background="#e6f7ff",width=100)
        kayit_frame.pack(pady=10,padx=15, side=tk.TOP)


        # Save settings button
        self.save_button = ttk.Button(kayit_frame, text="Ayarları Kaydet", command=self.save_settings)
        self.save_button.pack(pady=5,padx=5, side=tk.LEFT)

        # Load settings button
        self.load_button = ttk.Button(kayit_frame, text="Ayarları Yükle", command=self.load_settings)
        self.load_button.pack(pady=5,padx=5, side=tk.LEFT)

        # Frame for the duration input
        self.infoframe = tk.Frame(config_frame, background="#e6f7ff",)
        self.infoframe.pack(side=tk.TOP,pady=5)

        # Remaining time label
        self.remaining_time_label = ttk.Label(self.infoframe, text="Kalan Süre: --:--")
        self.remaining_time_label.pack(pady=5,padx=5,  side= tk.LEFT)

        # Kesilen yaratık label
        self.kesilen_yaratik_label = ttk.Label(self.infoframe, text="Kesilen Yaratık: 0")
        self.kesilen_yaratik_label.pack(pady=5,padx=5,  side= tk.LEFT)

        # Status label
        self.status_label = ttk.Label(config_frame, text="Durum: " + status_text)
        self.status_label.pack(pady=10,  side= tk.TOP)

        # Frame for the duration input
        self.kontrolframe = tk.Frame(config_frame, background="#e6f7ff",)
        self.kontrolframe.pack(side=tk.TOP,pady=5)

        # Start button
        self.start_button = ttk.Button(self.kontrolframe, text="Baslat", command=self.start_thread)
        self.start_button.pack(pady=5,padx=5,  side= tk.LEFT)

        # Stop button
        self.stop_button = ttk.Button(self.kontrolframe, text="Durdur", command=self.stop_thread_signal)
        self.stop_button.pack(pady=5,padx=5,  side= tk.LEFT)






        # Frame for the duration input
        duration_frame = tk.Frame(config_frame, background="#e6f7ff",)
        duration_frame.pack(side=tk.TOP,pady=5)

        # Label for duration
        self.duration_label = ttk.Label(duration_frame, background="#e6f7ff", text="Kesim Süresi (dakika):")
        self.duration_label.pack(pady= 3, side=tk.LEFT)

        # Entry for duration
        self.duration_entry = ttk.Entry(duration_frame, width=5)
        self.duration_entry.pack(padx=3,side=tk.LEFT)
        # Stil tanımlaması (background rengi ayarı)

        style = ttk.Style()
        style.configure('Custom.TFrame', background="#e6f7ff", relief='sunken', borderwidth=3)
        style.configure('Custom.TLabel', background="#e6f7ff")
        style.configure('Custom.TCheckbutton', background="#e6f7ff")
        style.configure('Custom.TRadiobutton', background="#e6f7ff")

        # Combobox için özel stil tanımla
        style.map('CustomCombobox.TCombobox',
                  fieldbackground=[('readonly', '#ffffff')],  # Readonly durumunda arka plan rengi
                  background=[('readonly', '#ffffff')],  # Readonly durumunda dış arka plan rengi
                  selectbackground=[('readonly', '#ffffff')],  # Seçilen öğenin arka plan rengi
                  selectforeground=[('readonly', '#333333')])  # Seçilen öğenin yazı rengi

        # Combobox için özel stil tanımla
        style.map('LightGreen.TCombobox',
                  fieldbackground=[('readonly', '#e0f2f1')],  # Readonly durumunda arka plan rengi (hafif yeşil)
                  background=[('readonly', '#ffffff')],  # Readonly durumunda dış arka plan rengi
                  selectbackground=[('readonly', '#e0f2f1')],  # Seçilen öğenin arka plan rengi
                  selectforeground=[('readonly', '#333333')])  # Seçilen öğenin yazı rengi

        myvalues = ["Eldiv Büyücüsü[12-13]", "Dişi Krofdor Savaşçısı[13]", "Zufen Ruhu[15]" , "Neferto[15]", "Kızıl Kanat[16]","Okcu Zarlog[17]","Avcı Morina[17]"]

        dropdown_frame1_main = tk.Frame(config_frame, background="#e6f7ff")
        dropdown_frame1_main.pack(side=tk.TOP, padx=5)

        # Dropdown Frame
        dropdown_frame1 = tk.Frame(dropdown_frame1_main, background="#e6f7ff")
        dropdown_frame1.pack(side=tk.LEFT, padx=5)

        dropdown_frame2 = tk.Frame(dropdown_frame1_main, background="#e6f7ff")
        dropdown_frame2.pack(side=tk.LEFT, padx=10)

        # Yaratık Tercih 1 Dropdown
        self.label1 = ttk.Label(dropdown_frame1, text="Yaratık Tercih 1:", background="#e6f7ff")
        self.label1.pack()
        self.combobox1 = ttk.Combobox(dropdown_frame1, values=myvalues, state='readonly', style='CustomCombobox.TCombobox')
        self.combobox1.pack()

        # Yaratık Tercih 2 Dropdown
        self.label2 = ttk.Label(dropdown_frame2, text="Yaratık Tercih 2:", background="#e6f7ff")
        self.label2.pack()
        self.combobox2 = ttk.Combobox(dropdown_frame2, values=myvalues, state='readonly', style='CustomCombobox.TCombobox')
        self.combobox2.pack()

        # Ayarlar için genişletilebilir panel
        self.expandable_frame = tk.Frame(config_frame, background="#e6f7ff")

        # '+/-' Butonu
        self.toggle_button = ttk.Button(config_frame, text='Ayarları Göster', command=self.toggle_settings)
        self.toggle_button.pack(pady=10)

        self.settings_visible = False

        sys.stdout = TextRedirector(self.log_text, log_queue)

        ## 🔥 İksir Ayarları Başlığı ve Listesi
        potion_settings_frame = tk.Frame(self.expandable_frame, background="#e6f7ff")
        potion_settings_frame.pack(pady=8, side=tk.TOP)

        # İksir Ayarları Başlığı
        self.potion_settings_label = ttk.Label(potion_settings_frame, text="Mevcut İksir Ayarlarınız", background="#e6f7ff", font=("Arial", 12, "bold"))
        self.potion_settings_label.pack(pady=2, side=tk.TOP)

        # İksir Ayarları Listesi
        potion_settings_text = (
            "CEP 1-2  : Güç İksiri\n"
            "CEP 3-4-5-6 : Hayat İksiri (Can < %65)\n"
            "CEP 7-8  : Mana İksiri (Mana < %55)\n"
            "CEP 9 : Acil Durum Dev İksiri (Rakip Sayısı > 1 veya Can < %25)\n"
            "CEP 10 : Acil Durum Bilgelik-Öfke İksiri (Rakip Sayısı > 1 veya Can < %25)\n"
            "CEP 11   : Serbest"
        )

        self.potion_settings_list = ttk.Label(
            potion_settings_frame,
            text=potion_settings_text,
            background="#e6f7ff",
            justify="left",
            anchor="w"
        )
        self.potion_settings_list.pack()

        ## 🔥 İksir Ayarları Başlığı ve Listesi
        self.setting_lineone_frame = tk.Frame(self.expandable_frame, background="#e6f7ff")
        self.setting_lineone_frame.pack(pady=5, side=tk.TOP)

        ## 🔥 İksir Ayarı Tercihleriniz
        potion_preferences_frame = ttk.Frame(self.setting_lineone_frame , style='Custom.TFrame')
        potion_preferences_frame.pack(padx=4,pady=10, fill='both', side=tk.LEFT)

        # İksir Ayarı Tercihleriniz Başlığı
        self.potion_preferences_label = ttk.Label(
            potion_preferences_frame,
            text="İksir Ayarı Tercihleriniz",
            font=("Arial", 12, "bold"),
            style = 'Custom.TLabel'
        )
        self.potion_preferences_label.pack(pady=5, side=tk.TOP)

        # İksir tercihleri seçenekleri
        self.first_turn_mana = tk.BooleanVar()
        self.first_turn_health = tk.BooleanVar()
        self.first_turn_wisdom_anger = tk.BooleanVar()


        # Checkbox 1: İlk tur mana iksiri basılsın
        self.checkbox1 = ttk.Checkbutton(
            potion_preferences_frame,
            text="İlk tur mana iksiri basılsın (CEP 6)",
            variable=self.first_turn_mana,
            style='Custom.TCheckbutton',
            onvalue=True,
            offvalue=False
        )
        self.checkbox1.pack(anchor="w", pady=2, padx=2)

        # Checkbox 2: İlk tur hayat iksiri basılsın
        self.checkbox2 = ttk.Checkbutton(
            potion_preferences_frame,
            text="İlk tur hayat iksiri basılsın (CEP 8)",
            variable=self.first_turn_health,
            style='Custom.TCheckbutton',
            onvalue=True,
            offvalue=False
        )
        self.checkbox2.pack(anchor="w", pady=2, padx=2)

        # Checkbox 3: İlk tur bilgelik-öfke iksiri basılsın
        self.checkbox3 = ttk.Checkbutton(
            potion_preferences_frame,
            text="İlk tur bilgelik-öfke iksiri basılsın (CEP 10)",
            variable=self.first_turn_wisdom_anger,
            style='Custom.TCheckbutton',
            onvalue=True,
            offvalue=False
        )
        self.checkbox3.pack(anchor="w", pady=2, padx=2)

        # Süper Vuruş Ayarları Frame'i
        super_hit_settings_frame = ttk.Frame(self.setting_lineone_frame, style='Custom.TFrame')
        super_hit_settings_frame.pack(padx=2,pady=10, fill='both', side=tk.LEFT)

        # Süper Vuruş Ayarları Başlığı
        super_hit_settings_label = ttk.Label(
            super_hit_settings_frame,
            text="Süper Vuruş Ayarlarınız",
            font=("Arial", 12, "bold"),
            style='Custom.TLabel'
        )
        super_hit_settings_label.pack(pady=5, side=tk.TOP)

        # Süper Vuruş Ayarları için Seçenekler
        super_hit_options = ["ust", "duz", "alt"]


        # Radio Button için ortak variable
        self.super_hit_selection = tk.IntVar(value=0)  # Başlangıçta hiçbir seçenek seçili değil

        # İlk Sıra için Frame
        self.first_row_frame = ttk.Frame(super_hit_settings_frame)
        self.first_row_frame.pack(fill='x', padx=4)

        # İlk Sıra için Radio Button
        super_hit_row1_radio = ttk.Radiobutton(
            self.first_row_frame,
            text="Süper Vuruş Seçeneği 1:",
            variable=self.super_hit_selection,
            value=1,  # Bu radio button seçildiğinde variable 1 değerini alır
            style='Custom.TRadiobutton'
        )
        super_hit_row1_radio.pack(side=tk.LEFT)

        # İlk Sıra için Dropdown'lar
        for i in range(4):
            combobox = ttk.Combobox(self.first_row_frame, values=super_hit_options, state='readonly', width=1 , style='LightGreen.TCombobox')
            combobox.pack(side=tk.LEFT, padx=1)

        # İkinci Sıra için Frame
        self.second_row_frame = ttk.Frame(super_hit_settings_frame)
        self.second_row_frame.pack(fill='x', padx=4)

        # İkinci Sıra için Radio Button
        super_hit_row2_radio = ttk.Radiobutton(
            self.second_row_frame,
            text="Süper Vuruş Seçeneği 2:",
            variable=self.super_hit_selection,
            value=2,  # Bu radio button seçildiğinde variable 2 değerini alır
            style='Custom.TRadiobutton'
        )
        super_hit_row2_radio.pack(side=tk.LEFT)

        # İkinci Sıra için Dropdown'lar
        for i in range(5):
            combobox = ttk.Combobox(self.second_row_frame, values=super_hit_options, state='readonly', width=1 , style='LightGreen.TCombobox')
            combobox.pack(side=tk.LEFT, padx=1)

            # Genel Ayarlar Frame'i
        self.general_settings_frame = ttk.Frame(self.setting_lineone_frame, style='Custom.TFrame')
        self.general_settings_frame.pack(padx=5,pady=10, fill='both', side=tk.LEFT)

        # Genel Ayarlar Başlığı
        general_settings_label = ttk.Label(
            self.general_settings_frame,
            text="Genel Ayarlar",
            font=("Arial", 12, "bold"),
            style='Custom.TLabel'
        )
        general_settings_label.pack(pady=4, padx=3, side=tk.TOP)

        self.general_first_row_frame = ttk.Frame(self.general_settings_frame)
        self.general_first_row_frame.pack(fill='x', padx=4, side=tk.TOP)

        # Trol Gücü Tuşu Dropdown Seçeneği
        self.troll_power_key_label = ttk.Label(
            self.general_first_row_frame,
            text="Trol Gücü Tuşu:",
            style='Custom.TLabel'
        )
        self.troll_power_key_label.pack(side=tk.LEFT, padx=3, pady=3)

        self.troll_power_key = ttk.Combobox(
            self.general_first_row_frame,
            values=["a", "s"],
            state='readonly',
            width=3,
            style='CustomCombobox.TCombobox'
        )
        self.troll_power_key.pack(side=tk.LEFT, padx=3, pady=3)
        self.troll_power_key.set("a")  # Setting default value to 'a'

        self.general_second_row_frame = ttk.Frame(self.general_settings_frame)
        self.general_second_row_frame.pack(fill='x', padx=4, side=tk.TOP)

        # Label for Aura Delay
        aura_delay_label = ttk.Label(self.general_second_row_frame , text="Aura Geciktirme:", background="#e6f7ff", style='Custom.TLabel')
        aura_delay_label.pack(side=tk.LEFT, padx=3, pady=3)

        # Dropdown for Aura Delay
        self.aura_delay_dropdown = ttk.Combobox(self.general_second_row_frame , values=[0, 1, 2, 3, 4, 5], state='readonly', width=3,
                                                style='CustomCombobox.TCombobox')
        self.aura_delay_dropdown.pack(side=tk.LEFT, padx=3, pady=3)
        self.aura_delay_dropdown.set(0)  # Set the default value to 1

    def get_aura_delay(self):
        """Retrieve the currently selected value from the Aura Delay dropdown."""
        return self.aura_delay_dropdown.get()

    def get_troll_power_key(self):
        """Returns the currently selected value from the 'Troll Power Key' dropdown."""
        return self.troll_power_key.get()

    def toggle_settings(self):
        if self.settings_visible:
            self.expandable_frame.pack_forget()
            self.toggle_button.configure(text='Ayarları Göster')
            self.settings_visible = False
        else:
            self.expandable_frame.pack(pady=10, padx=25, fill=tk.BOTH, expand=True)
            self.toggle_button.configure(text='Ayarları Gizle')
            self.settings_visible = True

    def save_settings(self):
        with open('settings.txt', 'w') as file:
            file.write(f"Duration: {self.duration_entry.get()}\n")
            file.write(f"First Choice: {self.combobox1.get()}\n")
            file.write(f"Second Choice: {self.combobox2.get()}\n")
            file.write(f"First Turn Mana: {self.first_turn_mana.get()}\n")
            file.write(f"First Turn Health: {self.first_turn_health.get()}\n")
            file.write(f"First Turn Wisdom-Anger: {self.first_turn_wisdom_anger.get()}\n")
            file.write(f"Troll Power Key: {self.troll_power_key.get()}\n")
            file.write(f"Super Hit Selection: {self.super_hit_selection.get()}\n")
            file.write(f"Aura Delay: {self.aura_delay_dropdown.get()}\n")  # Save the Aura Delay setting

            # Save each dropdown selection in the super hit rows
            first_row_values = [combobox.get() for combobox in self.first_row_frame.winfo_children() if
                                isinstance(combobox, ttk.Combobox)]
            second_row_values = [combobox.get() for combobox in self.second_row_frame.winfo_children() if
                                 isinstance(combobox, ttk.Combobox)]
            file.write(f"First Row Values: {','.join(first_row_values)}\n")
            file.write(f"Second Row Values: {','.join(second_row_values)}\n")

    def load_settings(self):
        try:
            with open('settings.txt', 'r') as file:
                lines = file.readlines()
                self.duration_entry.delete(0, tk.END)
                self.duration_entry.insert(0, lines[0].split(': ')[1].strip())
                self.combobox1.set(lines[1].split(': ')[1].strip())
                self.combobox2.set(lines[2].split(': ')[1].strip())
                self.first_turn_mana.set(eval(lines[3].split(': ')[1].strip()))
                self.first_turn_health.set(eval(lines[4].split(': ')[1].strip()))
                self.first_turn_wisdom_anger.set(eval(lines[5].split(': ')[1].strip()))
                self.troll_power_key.set(lines[6].split(': ')[1].strip())
                self.super_hit_selection.set(int(lines[7].split(': ')[1].strip()))
                self.aura_delay_dropdown.set(lines[8].split(': ')[1].strip())  # Load the Aura Delay setting

                # Load each dropdown selection in the super hit rows
                first_row_values = lines[9].split(': ')[1].strip().split(',')
                for combobox, value in zip([combobox for combobox in self.first_row_frame.winfo_children() if
                                            isinstance(combobox, ttk.Combobox)], first_row_values):
                    combobox.set(value)

                second_row_values = lines[10].split(': ')[1].strip().split(',')
                for combobox, value in zip([combobox for combobox in self.second_row_frame.winfo_children() if
                                            isinstance(combobox, ttk.Combobox)], second_row_values):
                    combobox.set(value)
        except FileNotFoundError:
            print("Settings file not found.")

    def get_super_hit_selection(self):
        # Süper vuruş tipini kontrol et
        super_hit_type = self.super_hit_selection.get()  # Hangi süper vuruş tipinin seçili olduğunu al

        # Eğer ilk sıra seçiliyse, ilk sıra dropdownlarının değerlerini topla
        if super_hit_type == 1:  # İlk sıra seçiliyse
            first_row_values = [widget.get() for widget in self.first_row_frame.winfo_children() if
                                isinstance(widget, ttk.Combobox)]
            return super_hit_type, first_row_values

        # Eğer ikinci sıra seçiliyse, ikinci sıra dropdownlarının değerlerini topla
        elif super_hit_type == 2:  # İkinci sıra seçiliyse
            second_row_values = [widget.get() for widget in self.second_row_frame.winfo_children() if
                                 isinstance(widget, ttk.Combobox)]
            return super_hit_type, second_row_values

        # Hiçbir süper vuruş tipi seçili değilse
        return 1, [["ust"],["ust"],["ust"],["ust"]]

    def returnimges(self):
        selected_value1 = self.combobox1.get()  # combobox1'in seçili değerini al
        selected_value2 = self.combobox2.get()  # combobox1'in seçili değerini al

        image_temps = []

        myvalues = ["Eldiv Büyücüsü[12-13]","Dişi Krofdor Savaşçıcı[13]", "Neferto[15]", "Kızıl Kanat[16]"]

        if selected_value1 == "Eldiv Büyücüsü[12-13]":
            for i in range(1,5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[0][i]))
        if selected_value1 == "Dişi Krofdor Savaşçısı[13]":
            for i in range(1, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[1][i]))
        if selected_value1 == "Zufen Ruhu[15]":
            for i in range(1, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[2][i]))
        if selected_value1 == "Neferto[15]":
            for i in range(1, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[3][i]))
        if selected_value1 == "Kızıl Kanat[16]":
            for i in range(1, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[4][i]))
        if selected_value1 == "Okcu Zarlog[17]":
            for i in range(1, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[5][i]))
        if selected_value1 == "Avcı Morina[17]":
            for i in range(1, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[6][i]))

        if selected_value2 == "Eldiv Büyücüsü[12-13]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[0][i]))
        if selected_value2 == "Dişi Krofdor Savaşçısı[13]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[1][i]))
        if selected_value2 == "Zufen Ruhu[15]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[2][i]))
        if selected_value2 == "Neferto[15]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[3][i]))
        if selected_value2 == "Kızıl Kanat[16]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[4][i]))
        if selected_value2 == "Okcu Zarlog[17]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[5][i]))
        if selected_value2 == "Avcı Morina[17]":
            for i in range(4, 5):
                image_temps.append(self.decode_base64_to_image_temps(base64_image_vals[6][i]))

        return image_temps

    def decode_base64_to_image_temps(self, base64_string):
        """Base64 string'i projenin dizininde temp klasörüne kaydeder."""

        # 1️⃣ Geçerli çalışma dizinini al ve "temp" klasörünü oluştur
        project_dir = os.getcwd()  # Geçerli çalışma dizinini al
        temp_dir = os.path.join(project_dir, 'temp')  # temp klasör yolu
        os.makedirs(temp_dir, exist_ok=True)  # temp klasörü oluştur (varsa hata vermez)

        # 2️⃣ Base64 string'i binary veriye çevir
        image_data = base64.b64decode(base64_string)  # Base64'ü binary veriye çevir

        # 3️⃣ Dosya adını oluştur (benzersiz olmalı)
        file_name = f"temp_{len(os.listdir(temp_dir)) + 1}.png"  # Benzersiz dosya adı
        file_path = os.path.join(temp_dir, file_name)  # Tam dosya yolu

        # 4️⃣ Görüntü verisini dosyaya kaydet
        with open(file_path, 'wb') as temp_file:
            temp_file.write(image_data)  # Görüntü verisini yaz

        #print(f"Geçici dosya oluşturuldu: {file_path}")  # Dosyanın yolunu yazdır
        return file_path  # Dosya yolunu döndür

    def temizle_temp_klasoru(self):
        """Temp klasörünü ve içindeki tüm dosyaları sil."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)  # temp klasörünü ve içindeki dosyaları sil
            #print(f"Temp klasörü silindi: {self.temp_dir}")

    def update_remaining_time(self):
        if self.updating_time:
            self.remaining_time = max(0, self.end_time - time.time())
            if self.remaining_time > 0:
                minutes, seconds = divmod(int(self.remaining_time), 60)
                self.remaining_time_label.config(text=f"Kalan Süre: {minutes:02}:{seconds:02}")
                self.tab.after(1000, self.update_remaining_time)  # 1 saniye sonra tekrar çalıştır
            else:
                self.remaining_time_label.config(text="Kalan Süre: 00:00")
                self.updating_time = False
                self.stop_thread_signal("Zaman doldu.")


        else:
            self.remaining_time_label.config(text="Kalan Süre: 00:00")

    def start_thread(self):
        if base64imagecheck():
            if not hasattr(self, 'thread') or not self.thread.is_alive():
                try:
                    duration = int(self.duration_entry.get())
                    self.remaining_time = duration * 60  # Süreyi saniye cinsinden kaydet
                    self.end_time = time.time() + self.remaining_time  # Kesim süresinin bitiş zamanını hesapla
                    self.updating_time = True
                    self.update_remaining_time()  # Kalan süreyi güncelle
                    self.stop_thread.clear()
                    self.kesilen_yaratik_count = 0  # Reset the count when the bot starts
                    self.kesilen_yaratik_label.config(text="Kesilen Yaratık: 0")  # Update the label
                    self.thread = threading.Thread(target=self.target, args=(self.stop_thread,))
                    self.thread.start()
                    self.status_label.config(text="Durum: Bot başladı")

                except ValueError:
                    print("Please enter a valid number for the duration.")
                    self.stop()

    def stop_thread_signal(self, message="Durdur tuşuna basıldı.", epin_reason=False):
        spammer.stop_spamming()
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.stop_thread.set()
            self.status_label.config(text="Durum: Bot başlamadı")
            self.remaining_time = 0  # Kalan süreyi sıfırla
            self.updating_time = False  # Geri sayımı durdur
            self.update_remaining_time()  # Ekranda kalan süreyi güncelle

            # EPIN nedeniyle durduysa özel bir mesaj göster
            if epin_reason:
                log_message("EPIN kesim hakkı yok. Bot durduruldu.")
            else:
                log_message(message)

    def stop(self):
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.stop_thread_signal()
            if hasattr(self, 'thread') and self.thread.is_alive():
                self.thread.join()

    def update_kesilen_yaratik_count(self):
        self.kesilen_yaratik_count += 1
        self.kesilen_yaratik_label.config(text=f"Kesilen Yaratık: {self.kesilen_yaratik_count}")


class iksir:
    def __init__(self, kesim_kontrol_in_fonk):
        self.iksir_aktiflik = [7, 7, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1]
        # self.iksir_aktiflik = [1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1]

        self.kesim_kontrol_in = kesim_kontrol_in_fonk

        self.iksir_kurallar = [[6, [1, 2], 1], [5, [9], 0], [4, [3, 4, 5, 6], 0],
                               [7, [7, 8], 1]]  # , [3,[8],0], [8,[6],0], [9,[0],0]]

        self.last_usage_times = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.log_queue = log_queue

        print(self.iksir_aktiflik)
        print(self.last_usage_times)
        # 0 serbest cep
        # 1 her tur bas
        # 2 x turda bir bas, ilk tur basmaz, zaman sınırı yok
        # 3 dovus basi 1 kere bas mana iksiri
        # 8 dovus basi 1 kere bas can iksiri
        # 4 can iksiri (can %70) - Zaman sınırı 20sn
        # 5 acil durum (can %20 asagisi)
        # 6 guc iksiri x turda bir bas, ilk tur basar18
        # 7 mana iksiri - x turda bir bas, ilk tur basmaz, - Zaman sınırı 20sn
        # 9 ilk tur bilgelik bas

    def ilkturappend(self):
        self.iksir_kurallar = [[6, [1, 2], 1], [4, [3, 4, 5, 6], 0],
                               [7, [7, 8], 1]]  # , [3,[8],0], [8,[6],0], [9,[0],0]]

        if self.kesim_kontrol_in.first_turn_mana.get():
            self.iksir_kurallar.append([3, [8], 0])
        if self.kesim_kontrol_in.first_turn_health.get():
            self.iksir_kurallar.append([8, [6], 0])

        if self.kesim_kontrol_in.first_turn_wisdom_anger.get():
            self.iksir_kurallar.append([9, [0], 0])
            self.iksir_kurallar.append([5, [9], 0])
        else:
            self.iksir_kurallar.append([5, [9,0], 0])

    def iksir_ic(self, tur_sayisi, can_durumu, mana, sayi, guc):
        print(self.iksir_aktiflik)
        print(self.last_usage_times)
        print(time.time())

        current_time = time.time()
        for i, deger in enumerate(self.iksir_kurallar):
            for j in deger[1]:
                if self.iksir_aktiflik[j - 1] != 0:  # Aktif ise
                    kural = deger[0]
                    kural3 = deger[2]
                    if 0 == kural:  # Serbest cep
                        time.sleep(0.1)
                    elif 1 == kural:  # Her tur bas
                        pyautogui.press(str(j))
                    elif 2 == kural and tur_sayisi % kural3 == 0 and tur_sayisi != 0:  # x turda bir bas
                        if (self.iksir_aktiflik[j - 1] != 0):
                            pyautogui.press(str(j))
                            time.sleep(0.2 + random.uniform(-0.04, 0.04))
                            self.iksir_aktiflik[j - 1] = self.iksir_aktiflik[j - 1] - 1
                            time.sleep(0.2 + random.uniform(-0.04, 0.04))
                            break

                    elif 7 == kural and tur_sayisi % kural3 == 0 and tur_sayisi != 0 and mana < 70:  # x turda bir bas
                        if (self.iksir_aktiflik[j - 1] != 0):
                            if time.time() - self.last_usage_times[kural - 1] >= 19:  # Check if 16 seconds have passed
                                pyautogui.press(str(j))
                                time.sleep(0.06 + random.uniform(-0.04, 0.04))
                                self.iksir_aktiflik[j - 1] = self.iksir_aktiflik[j - 1] - 1
                                self.last_usage_times[kural - 1] = time.time()  # Update the last usage time
                                time.sleep(0.06 + random.uniform(-0.04, 0.04))
                                break

                    elif 3 == kural and tur_sayisi == 0:  # Dövüş başı 1 kere bas mana
                        if (self.iksir_aktiflik[j - 1] > 0):
                            pyautogui.press(str(j))
                            time.sleep(0.10 + random.uniform(-0.05, 0.05))
                            self.iksir_aktiflik[j - 1] = self.iksir_aktiflik[j - 1] - 1
                            self.last_usage_times[6] = time.time()  # MANA
                            time.sleep(0.10 + random.uniform(-0.05, 0.05))

                    elif 9 == kural and tur_sayisi == 0:  # Dövüş başı 1 kere bas 10. cep
                        if (self.iksir_aktiflik[9] > 0):
                            pyautogui.press(str(0))
                            self.iksir_aktiflik[9] = self.iksir_aktiflik[9] - 1
                            time.sleep(0.07 + random.uniform(-0.05, 0.05))

                    elif 8 == kural and tur_sayisi == 0:  # Dövüş başı 1 kere bas can
                        if (self.iksir_aktiflik[j - 1] > 0):
                            pyautogui.press(str(j))
                            time.sleep(0.10 + random.uniform(-0.05, 0.05))
                            self.iksir_aktiflik[j - 1] = self.iksir_aktiflik[j - 1] - 1
                            self.last_usage_times[3] = time.time()  # CAN
                            time.sleep(0.10 + random.uniform(-0.05, 0.05))

                    elif ((5 == kural and can_durumu <= 25) or (
                            5 == kural and sayi != 1)) and not zafer():  # Acil durum (can %20 altında) ve rakip 1'den fazla
                        if (self.iksir_aktiflik[j - 1] == 1):
                            pyautogui.press(str(j))
                            time.sleep(0.19 + random.uniform(-0.04, 0.04))
                            if not self.kesim_kontrol_in.first_turn_wisdom_anger.get():
                                pyautogui.press(str(0))  # ilk tur bilgelik basılacaksa kapat
                                self.iksir_aktiflik[9] = self.iksir_aktiflik[9] - 1
                                time.sleep(0.7 + random.uniform(-0.04, 0.04))
                            self.iksir_aktiflik[j - 1] = 0
                            time.sleep(0.19 + random.uniform(-0.04, 0.04))
                            sayac_acil_durum = 0
                            while can_durumu < 40 and sayac_acil_durum < 20:
                                health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                can_durumu = health
                                if can_durumu >= 40:
                                    break
                                iksir.iksir_ic(self,tur_sayisi, health, mana, sayi, 0)
                                time.sleep(0.4)
                                sayac_acil_durum += 1
                            break

                    elif 4 == kural and can_durumu <= 65 and not zafer():  # Can iksiri (can %55 altında)
                        print(time.time())
                        if time.time() - self.last_usage_times[kural - 1] >= 21:  # Check if 20 seconds have passed
                            if (self.iksir_aktiflik[j - 1] == 1):
                                pyautogui.press(str(j))
                                time.sleep(0.14 + random.uniform(-0.03, 0.03))
                                self.iksir_aktiflik[j - 1] = 0
                                self.last_usage_times[kural - 1] = time.time()  # Update the last usage time
                                time.sleep(0.14 + random.uniform(-0.03, 0.03))
                                if can_durumu < 40 and 21 - int(
                                        time.time() - self.last_usage_times[kural - 1]) > 1:
                                    for i in range(1, 1 + 21 - int(
                                            time.time() - self.last_usage_times[kural - 1])):
                                        print(1 + 21 - int(time.time() - self.last_usage_times[kural - 1]))
                                        time.sleep(1)
                                        health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                        can_durumu = health
                                        if can_durumu >= 30:
                                            break
                                    kontrol = 0
                                    for i in deger[1]:
                                        if self.iksir_aktiflik[i - 1] == 1:
                                            kontrol = 1
                                    if can_durumu < 40 and kontrol == 1:
                                        health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                        iksir.iksir_ic(self,tur_sayisi, health, mana, sayi, 0)
                            if can_durumu < 30:
                                time.sleep(3)
                                break
                        elif can_durumu < 35 and 21 - int(time.time() - self.last_usage_times[kural - 1]) > 1:
                            print("Can fazla azaldı, bekleniyor")
                            for i in range(1, 1 + 21 - int(time.time() - self.last_usage_times[kural - 1])):
                                print(1 + 21 - int(time.time() - self.last_usage_times[kural - 1]))
                                time.sleep(1)
                                health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                can_durumu = health
                                if can_durumu >= 35:
                                    break

                            kontrol = 0
                            for i in deger[1]:
                                if self.iksir_aktiflik[i - 1] == 1:
                                    kontrol = 1

                            if can_durumu < 30 and kontrol == 1:
                                health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                iksir.iksir_ic(self,tur_sayisi, health, mana, sayi, 0)
                        elif can_durumu >= 45:
                            print("Can yeterince yuksek %45 ")
                            break
                        else:
                            print("Aktif can iksiri var ve can yuksek %35-%45")
                            break


                        print("Can dongusu")
                    elif 6 == kural and tur_sayisi % kural3 == 0 and guc == 1:  # x turda bir bas, ilk tur basar
                        if (self.iksir_aktiflik[j - 1] > 0):
                            pyautogui.press(str(j))
                            time.sleep(0.05 + random.uniform(-0.04, 0.04))
                            self.iksir_aktiflik[j - 1] = self.iksir_aktiflik[j - 1] - 1
                            time.sleep(0.05 + random.uniform(-0.04, 0.04))
                            break

    def custom_rule_6(self, tursayisi, candurumu):
        if tursayisi % 3 == 0 and candurumu <= 70:
            return True
        return False

    def aktiflik_sifirla(self):
        print(self.iksir_aktiflik)
        print(self.last_usage_times)
        self.iksir_aktiflik = [7, 7, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1]
        self.last_usage_times = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]




def human_like_mouse_move(x, y, duration,sapmax=100,sapmay=100,adimsapmax1 = -70,adimsapmay1 = -50,adimsapmax2 = 70,adimsapmay2 = 50):
    """
    Moves the mouse to a target location (x, y) in a more human-like manner.
    Args:
    x (int): The x-coordinate of the target location.
    y (int): The x-coordinate of the target location.
    duration (float): The total time taken to move the mouse from the current location to the target location.
    """
    # Get the current mouse position
    start_x, start_y = pyautogui.position()

    # Calculate the distance to the target
    distance = ((x - start_x)**2 + (y - start_y)**2)**0.5
    steps = int(distance // 140)  # number of intermediate points, adjust if needed
    steps = max(steps, 1)  # ensure at least two steps

    # Calculate step duration and randomness factor
    randomness = 6  # max random deviation in pixels

    # Move the mouse
    for i in range(steps):
        intermediate_x = start_x + (x - start_x) * (i / steps) + random.randint(-randomness, randomness)
        intermediate_y = start_y + (y - start_y) * (i / steps) + random.randint(-randomness, randomness)
        pyautogui.dragTo(intermediate_x + random.randint(adimsapmax1, adimsapmax2), intermediate_y + random.randint(adimsapmay1, adimsapmay2), 0.01+random.uniform(0.01,0.05) , mouseDownUp=False)

    # Final move to the exact location

    kontrol1 = start_x - x
    kontrol2 = start_y - y

    if kontrol1 <= 0 and kontrol2 <= 0:
        pyautogui.dragTo(x+ random.randint(0, sapmax), y+ random.randint(0, sapmay), duration=0.2+random.uniform(0.01,0.05), mouseDownUp=False)
    elif kontrol1 >= 0 and kontrol2 <= 0:
        pyautogui.dragTo(x- random.randint(0, sapmax), y+ random.randint(0, sapmay), duration=0.2+random.uniform(0.01,0.05), mouseDownUp=False)
    elif kontrol1 <= 0 and kontrol2 >= 0:
        pyautogui.dragTo(x+ random.randint(0, sapmax), y- random.randint(0, sapmay), duration=0.2+random.uniform(0.01,0.05), mouseDownUp=False)
    elif kontrol1 >= 0 and kontrol2 >= 0:
        pyautogui.dragTo(x- random.randint(0, sapmax), y- random.randint(0, sapmay), duration=0.2+random.uniform(0.01,0.05), mouseDownUp=False)

    pyautogui.dragTo(x, y,duration=0.04, mouseDownUp=False)

def log_message(message):
    logs.config(state=tk.NORMAL)
    logs.insert(tk.END, f"{message}\n")
    logs.config(state=tk.DISABLED)
    logs.see(tk.END)

def base64imagecheck():
    """# Decode the base64 string from utf-8
    #base64_str = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAAHACMDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDJ8WfFLwN4p+BPin4Wm41GHSND8IKNG1OW2QQz6jpr+a7LGq743uGl8tnbA2oTwW50PCHjTTNJ8WfBPR/Fdt4c1bw7pa3Mut63Jpga8vtQm067YRMqwL+4haQRqRksUVyBgEFFeBQrSlT5mkbuKOL/AGd9T8P/ANtf214lisf7S1DVdNXU9KS18nT7fShahd8UaRSb33AgoSueuSSSL914i8LQ/DebTPBfhTw/q8FvNrdpqS6y08G4NO4hddsTs+2LZty6ldoFFFVQqOSV0LlR2GufFLwrqDaZKmoO2NI06JisMoG5LOFGHQdCpH4UUUVxTrz5mLlR/9k="
    base64_str = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAGCAYAAADUtS5UAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAHZSURBVChTTVLJbhNREOw3IguOx3Yc4COAKxDEhQtCSIgLV7jwFXBG/ACfwYEv4IgQQmIRihKRKODE+zoz9rPHM/a46HoTCw59eL1UV9VribrnKPgGz14Knr/6FzfvCi4XBdlyCTvqIurVEXRq2NHe2w8FxYognceIbYhpNEB4gbOxKZhPx/quu/mo18AlzbHGuLGf44oddbBTMrh+R4uaKPh5sHlQP0YaW5T3PNdDkFHz1AHceywoVY3L8z3uN9H7cwhjlOwihQ16LmZKiov+F5PEU8giiVEsc1hgw75TN2ycwHiC1vF3TIYdp5oq4kmA8aCFjS1VXFaAmdXaAlmWYTYe5XO6eJVpv40cLmP/keDWA1GSohihq8tiPlNFBvefCvxdAxKZDNtu8fnBJwSt36he81C5alDSPvZsbqsbuoRulaqeU04C67lUFRHH3xW8/SB48oLu5A6SPGeEiqoKWtnL/22ZJkhUHQHOfn7EUJtJjCAcLl8RbBfoxjenkLWK5ugIF3KOf75ardzM63cUJGj++nrR78HXPdKvHTkmjKBdcyrIfktVUQntpr08olTdoa3rWv3wM1oK2D75gVAPb7047J458lz45n1OuHH0RW/gAJHeQhJb/AVDZcPeVAk1CQAAAABJRU5ErkJggg=="
    base64_bytes = base64_str.encode('utf-8')
    image_data = base64.b64decode(base64_bytes)
    template = Image.open(io.BytesIO(image_data))
    open_cv_image = np.array(template)
    template = np.array(template)
    template = template[:, :, ::-1].copy()  # Convert RGB to BGR for OpenCV

    # Convert template to grayscale
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Take a screenshot of the screen
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = screenshot[:, :, ::-1].copy()  # Convert RGB to BGR for OpenCV

    # Convert screenshot to grayscale
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    threshold = 0.8  # You can adjust this value
    if max_val >= threshold:
        return True
    else:
        return False"""
    return True

class KeySpammer:
    def __init__(self, key='w', spam_delay=0.15):
        self.key = key
        self.spam_delay = spam_delay
        self.stop_event = threading.Event()
        self.spam_thread = threading.Thread(target=self._spam_key)
        self.current_key = self.key  # Yeni eklenen

    def _spam_key(self):
        while not self.stop_event.is_set():
            pyautogui.press(self.current_key)
            time.sleep(round(random.uniform(self.spam_delay + 0.03, self.spam_delay + 0.11), 2))

    def start_spamming(self, key=None):
        if key is not None:
            self.current_key = key
        if not self.spam_thread.is_alive():
            self.stop_event.clear()
            self.spam_thread = threading.Thread(target=self._spam_key)
            self.spam_thread.start()
            print(f"Started spamming '{self.current_key}'. Press 'esc' to stop.")

    def stop_spamming(self):
        if self.spam_thread.is_alive():
            self.stop_event.set()
            self.spam_thread.join()
            print(f"Stopped spamming '{self.current_key}'.")
        else:
            print("Spam already stopped.")

    def is_alive(self):
        return self.spam_thread.is_alive()

def aurahazirlik(key,delaylevel):
    time.sleep((0.15 + int(delaylevel)*0.03) + round(random.uniform(-0.07, 0.12), 2))
    pyautogui.press(key)
    time.sleep((0.07 + int(delaylevel)*0.03) + round(random.uniform(-0.07, 0.12), 2))
    pyautogui.press('Tab')
    time.sleep((0.20 + int(delaylevel)*0.06) + round(random.uniform(-0.05, 0.07), 2))
    pyautogui.press('t')
    """pyautogui.press('0')
    time.sleep(0.24 + round(random.uniform(-0.07, 0.12), 2))"""

def savastan_cik(avlan,hizli_cikis):

    if hizli_cikis == 1:
        time.sleep(0.25 + random.uniform(-0.05, 0.05))
        human_like_mouse_move(avlan[0] - random.randint(26, 36), avlan[1] - random.randint(26, 36), 0.2)
        pyautogui.click(avlan[0] + random.randint(2, 18), avlan[1] + random.randint(2, 18))
        time.sleep(0.25 + random.uniform(-0.05, 0.05))
    else:
        cikis = imagesearch(image_path("cikis.png"))
        if cikis[0] == -1:
            sifirla = imagesearch(image_path("sifirla.png"))

            human_like_mouse_move(sifirla[0],
                                  sifirla[1], 0.3,
                                  55 + random.randint(5, 15),
                                  55 + random.randint(5, 15))

            pyautogui.click(sifirla[0]+random.randint(1,3), sifirla[1]+random.randint(1,3))

            human_like_mouse_move(sifirla[0]+150 + random.randint(-25, 25),
                                  sifirla[1]+100 + random.randint(-25, 25), 0.3,
                                  55 + random.randint(5, 15),
                                  55 + random.randint(5, 15))

            time.sleep(1 + random.uniform(-0.25, 0.5))
            cikis = imagesearch(image_path("cikis.png"))

        randsayi_1 = random.randint(1,100)

        if randsayi_1 % 1 == 0 and cikis[0] != -1:
            human_like_mouse_move(cikis[0],
                                  cikis[1], 0.3,
                                  55 + random.randint(5, 15),
                                  55 + random.randint(5, 15))
            pyautogui.click(cikis[0]+random.randint(1,3), cikis[1]+random.randint(1,3))

            time.sleep(0.25 + random.uniform(-0.05, 0.05))
            human_like_mouse_move(avlan[0]-random.randint(26,36), avlan[1]-random.randint(26,36), 0.2)
            pyautogui.click(avlan[0]+random.randint(2,18),avlan[1]+random.randint(2,18))
            time.sleep(0.25 + random.uniform(-0.05, 0.05))
        else:
            time.sleep(0.25 + random.uniform(-0.05, 0.05))
            human_like_mouse_move(avlan[0] - random.randint(26, 36), avlan[1] - random.randint(26, 36), 0.2)
            pyautogui.click(avlan[0] + random.randint(2, 18), avlan[1] + random.randint(2, 18))
            time.sleep(0.25 + random.uniform(-0.05, 0.05))

def zafer():
    zafer = imagesearch(image_path("zafer.png"))
    dovus_bitti = imagesearch(image_path("dovus_bitti.png"))
    code103 = imagesearch(image_path("code103.png"))

    if zafer[0] != -1 or dovus_bitti[0] != -1 or code103[0] != -1:
        time.sleep(0.20 + random.uniform(-0.15, 0.15))
        print("Dövüş bitti")
        return True
    print("Zafer kontrolü")

def find_situation():
#1 = search
#2 = fight
    print("Savaş modu - Arama modu analiz ediliyor")
    if imagesearch(image_path("Fight", "fightsw.png"))[0] == -1:
        print("Arama Moduna Geçiliyor")
        return 1
    else:
        print("Savaş Moduna Geçiliyor")
        return 0

def grab(q, ):
    golge = imagesearch(image_path("golge.png"))
    sayi = imagesearcharea(image_path("Rakip_Sayisi.png"),1150,198,1185,231,0.8)

    print(golge)

    try:
        can = ImageGrab.grab(bbox=(golge[0] + 40, golge[1] + 15, golge[0] + 162, golge[1] + 16))
        rakip_can = ImageGrab.grab(bbox=(golge[0] + 273, golge[1] + 15, golge[0] + 393, golge[1] + 16))
        mana = ImageGrab.grab(bbox=(golge[0] + 40, golge[1] + 24, golge[0] + 162, golge[1] + 25))

        canbar = cv2.cvtColor(numpy.array(can), cv2.COLOR_BGR2GRAY)
        ret, canbar = cv2.threshold(canbar, 15, 255, cv2.THRESH_BINARY)

        canbar2 = cv2.cvtColor(numpy.array(rakip_can), cv2.COLOR_BGR2GRAY)
        ret, canbar2 = cv2.threshold(canbar2, 15, 255, cv2.THRESH_BINARY)

        canbar3 = cv2.cvtColor(numpy.array(mana), cv2.COLOR_BGR2GRAY)
        ret, canbar3 = cv2.threshold(canbar3, 55, 255, cv2.THRESH_BINARY)

        # Görüntü üzerinde ikili eşikleme uygulayın
        black = 0
        black2 = 0
        black3 = 0

        pix = 122

        # print(can.getpixel(xy = (10,0)))

        for i in canbar[0]:
            if i == 0:
                black = black + 1
        for j in canbar2[0]:
            if j == 0:
                black2 = black2 + 1
        for x in canbar3[0]:
            if x == 0:
                black3 = black3 + 1

        percent = float("{:.2f}".format(100 - ((black / pix) * 100)))
        percent2 = float("{:.2f}".format(100 - ((black2 / pix) * 100)))
        percent3 = float("{:.2f}".format(100 - ((black3 / pix) * 100)))

        q.put(percent)  # Put the result in the queue
        q.put(percent2)  # Put the result in the queue
        q.put(percent3)  # Put the result in the queue

        if(sayi[0] != -1):
            q.put(1)
        else:
            q.put(2)




    except Exception as e:
        input(e)  # Kullanıcı ENTER'a basana kadar bekler

def calculateHealth_EnemyNumber():
    golge = imagesearch(image_path("golge.png"))

    if golge[0] == -1:
        time.sleep(1)
        while golge[0] == -1:
            golge = imagesearch(image_path("golge.png"))
            time.sleep(1)
            print("golge görünmüyor")

    if golge[0] != -1:
        print("Can hesaplanıyor")
        q = Queue()
        p2 = Process(target=grab, args=(q,))
        p2.start()
        p2.join()
        p2.terminate()

        percent = q.get()
        percent2 = q.get()
        percent3 = q.get()
        sayi = q.get()


        print(percent)

        return percent,percent2,percent3,sayi

    else:
        print("Golge Bulunamadı, gölge çağırmayın bozuluyor")
        return 0


log_queue = queue.Queue()
spammer = KeySpammer(key='q', spam_delay=0.15)
app_epin = ""

base64_image_vals = [
["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"
],
["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"
],
[
"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"
],
["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"
],
[
"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"
],
[
"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"
],
[
"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"

]
]

def main(stop_event):

    try:

        myiksir.ilkturappend()
        tip, kombinasyon = kesim_control.get_super_hit_selection()
        
        found = False

        time.sleep(2)

        if find_situation() == 0:
            found = True

        """kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')

        hWnd = kernel32.GetConsoleWindow()

        user32.MoveWindow(hWnd, 500, 950, 800, 200, True)"""

        time.sleep(2)

        Map = imagesearch(image_path("Harita.png"))

        avlan = imagesearch(image_path("PixelFinder", "avlan.png"))

        sayac = 0
        sayac1 = 0
        sayac2 = 0
        sayac3 = 0
        key_press_state = 0
        kesilen_slot = 0

        print(Map)

        selected_imgs = kesim_control.returnimges()

        if found==False:
            human_like_mouse_move(avlan[0],
                                  avlan[1], 0.3,
                                  55 + random.randint(5, 15),
                                  55 + random.randint(5, 15))
            pyautogui.click(avlan)
            time.sleep(1.5)



        while not stop_event.is_set():
            #pyautogui.click(945,213-randrange(0,25))
            #yaratık = randrange(0,25)
            #if yaratık % 2 == 1:
            time.sleep(0.75)
            bolge = 0
            x = 220
            y = 297
            harf = imagesearcharea(selected_imgs[0],220, 297, 1678, 761,0.70)
            if(harf[0] == -1):
                harf = imagesearcharea(selected_imgs[1],220, 297, 1678, 761,0.70)
            if (harf[0] == -1):
                harf = imagesearcharea(selected_imgs[2], 220, 297, 1678, 761,0.70)
            if (harf[0] == -1):
                harf = imagesearcharea(selected_imgs[3], 220, 297, 1678, 761,0.70)
            if (harf[0] == -1):
                harf = imagesearcharea(selected_imgs[4], 220, 297, 1678, 761,0.70)

            if harf[0] != -1 and harf[0] < 732 and harf[1] <= 248:
                bolge = 1
            elif harf[0] != -1 and harf[0] >= 732 and harf[1] <= 248:
                bolge = 2
            elif harf[0] != -1 and harf[0] < 732 and harf[1] > 248:
                bolge = 3
            elif harf[0] != -1 and harf[0] >= 732 and harf[1] > 248:
                bolge = 4

            savas_sonu = 0

            if harf[0] != -1:
                if(harf[1]+299 >= 299):
                    unlem = imagesearcharea(image_path("unlem.png"),harf[0]+220,harf[1]-60+297,harf[0]+80+220,harf[1]+15+297,0.980)

                    if unlem[0] != -1:
                        print("Yaratık bulundu ama unlem var - X1Y1")
                        x = 220
                        y = 297
                        harf = imagesearcharea(selected_imgs[0], 220, 297, 944, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[1], 220, 297, 944, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[2], 220, 297, 944, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[3], 220, 297, 944, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[4], 220, 297, 944, 528, 0.70)
                        if harf[0] != -1:
                            if (harf[1] + 299 >= 299):
                                unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y, harf[0] + 80 + x,
                                                        harf[1] + 15 + y, 0.980)
                                bolge = 1
                            else:
                                found = False
                                print("Yaratık bulundu ama pixel fazla yukarıda")

                    if unlem[0] != -1:
                        print("Yaratık bulundu ama unlem var - X2Y1")
                        x = 944
                        y = 297
                        harf = imagesearcharea(selected_imgs[0], 944, 297, 1678, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[1], 944, 297, 1678, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[2], 944, 297, 1678, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[3], 944, 297, 1678, 528, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[4], 944, 297, 1678, 528, 0.70)
                        if harf[0] != -1:
                            if (harf[1] + 299 >= 299):
                                unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y,harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                bolge = 2
                            else:
                                found = False
                                print("Yaratık bulundu ama pixel fazla yukarıda")

                    if unlem[0] != -1:
                        print("Yaratık bulundu ama unlem var - X1Y2")
                        x = 220
                        y = 528
                        harf = imagesearcharea(selected_imgs[0], 220, 528, 944, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[1], 220, 528, 944, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[2], 220, 528, 944, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[3], 220, 528, 944, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[4], 220, 528, 944, 761, 0.70)
                        if harf[0] != -1:
                            if (harf[1] + 299 >= 299):
                                unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y,harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                bolge = 3
                            else:
                                found = False
                                print("Yaratık bulundu ama pixel fazla yukarıda")

                    if unlem[0] != -1:
                        print("Yaratık bulundu ama unlem var - X2Y2")
                        x = 944
                        y = 528
                        harf = imagesearcharea(selected_imgs[0], 944, 528, 1678, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[1], 944, 528, 1678, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[2], 944, 528, 1678, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[3], 944, 528, 1678, 761, 0.70)
                        if (harf[0] == -1):
                            harf = imagesearcharea(selected_imgs[4], 944, 528, 1678, 761, 0.70)
                        if harf[0] != -1:
                            if (harf[1] + 299 >= 299):
                                unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y,harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                bolge = 4
                            else:
                                found = False
                                print("Yaratık bulundu ama pixel fazla yukarıda")

                    if unlem[0] == -1:
                        found = True
                        print("Yaratık bulundu")
                        human_like_mouse_move(harf[0] + 18 + random.randint(-2 , 2) + x,
                                              (harf[1] - 21 + random.randint(-2 , 2)) + y, 0.3,
                                              55 + random.randint(5, 15),
                                              55 + random.randint(5, 15))
                        pyautogui.click(harf[0] + 24 + x + random.randint(-1 , 1), (harf[1] - 24) + y + random.randint(-1 , 1))
                        time.sleep(round(random.uniform(0.06, 0.15), 2))
                        pyautogui.click(harf[0] + 26 + x + random.randint(-1 , 1), (harf[1] - 26) + y + random.randint(-1 , 1))
                        time.sleep(random.uniform(0.2, 0.4))
                        human_like_mouse_move(random.randint(940, 1600),
                                              random.randint(300, 800), 0.3,
                                              55 + random.randint(5, 15),
                                              55 + random.randint(5, 15))
                        time.sleep(0.75)

                        maptest = imagesearcharea(image_path("Harita.png"),760,146,930,270)
                        zaten_dovuste = imagesearcharea(image_path("iptal.png"), 182, 200, 1740, 863, 0.8)
                        kapat = imagesearch(image_path("kapat.png"))

                        if maptest[0] != -1 and bolge != 0:
                            found = False

                            if zaten_dovuste[0] != -1:
                                print("Zaten dovuste")
                                human_like_mouse_move(zaten_dovuste[0]+182+random.randint(-2,2),
                                                      zaten_dovuste[1]+200+random.randint(-2,2), 0.3,
                                                      55 + random.randint(5, 15),
                                                      55 + random.randint(5, 15))
                                time.sleep(0.2)

                                pyautogui.click(zaten_dovuste[0] + random.randint(1, 5) + 182, zaten_dovuste[1] + 200 + random.randint(1, 5))

                            elif kapat[0] != -1:
                                human_like_mouse_move(kapat[0],
                                                      kapat[1], 0.3,
                                                      55 + random.randint(5, 15),
                                                      55 + random.randint(5, 15))
                                time.sleep(0.2)

                                pyautogui.click(kapat[0] + random.randint(1, 5), kapat[1] + random.randint(1, 5))

                            if bolge != 1:
                                print("Dovus baslamadi araniyor - X1Y1")
                                x = 220
                                y = 297
                                harf = imagesearcharea(selected_imgs[0], 220, 297, 944, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[1], 220, 297, 944, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[2], 220, 297, 944, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[3], 220, 297, 944, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[4], 220, 297, 944, 528, 0.70)
                                if harf[0] != -1:
                                    if (harf[1] + 299 >= 299):
                                        found = True
                                        unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y, harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                        if unlem[0] != -1:
                                            print("Yaratık bulundu ama unlem var - devam1")
                                            found = False
                                    else:
                                        found = False
                                        print("Yaratık bulundu ama pixel fazla yukarıda")

                            if bolge != 2 and found == False:
                                print("Dovus baslamadi araniyor - X2Y1")
                                x = 944
                                y = 297
                                harf = imagesearcharea(selected_imgs[0], 944, 297, 1678, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[1], 944, 297, 1678, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[2], 944, 297, 1678, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[3], 944, 297, 1678, 528, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[4], 944, 297, 1678, 528, 0.70)
                                if harf[0] != -1:
                                    if (harf[1] + 299 >= 299):
                                        found = True
                                        unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y,harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                        if unlem[0] != -1:
                                            print("Yaratık bulundu ama unlem var - devam2")
                                            found = False
                                    else:
                                        found = False
                                        print("Yaratık bulundu ama pixel fazla yukarıda")

                            if bolge != 3 and found == False:
                                print("Dovus baslamadi araniyor - X1Y2")
                                x = 220
                                y = 528
                                harf = imagesearcharea(selected_imgs[0], 220, 528, 944, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[1], 220, 528, 944, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[2], 220, 528, 944, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[3], 220, 528, 944, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[4], 220, 528, 944, 761, 0.70)
                                if harf[0] != -1:
                                    if (harf[1] + 299 >= 299):
                                        found = True
                                        unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y,harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                        if unlem[0] != -1:
                                            print("Yaratık bulundu ama unlem var - devam3")
                                            found = False
                                    else:
                                        found = False
                                        print("Yaratık bulundu ama pixel fazla yukarıda")

                            if bolge != 4 and found == False:
                                print("Dovus baslamadi araniyor - X2Y2")
                                x = 944
                                y = 528
                                harf = imagesearcharea(selected_imgs[0], 944, 528, 1678, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[1], 944, 528, 1678, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[2], 944, 528, 1678, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[3], 944, 528, 1678, 761, 0.70)
                                if (harf[0] == -1):
                                    harf = imagesearcharea(selected_imgs[4], 944, 528, 1678, 761, 0.70)
                                if harf[0] != -1:
                                    if (harf[1] + 299 >= 299):
                                        found = True
                                        unlem = imagesearcharea(image_path("unlem.png"), harf[0] + x, harf[1] - 60 + y,harf[0] + 80 + x, harf[1] + 15 + y, 0.980)
                                        if unlem[0] != -1:
                                            print("Yaratık bulundu ama unlem var - devam4")
                                            found = False
                                    else:
                                        found = False
                                        print("Yaratık bulundu ama pixel fazla yukarıda")

                            if unlem[0] == -1 and found:
                                found = True
                                print("Yaratık bulundu")
                                human_like_mouse_move(harf[0] + 20 + random.randint(-2 , 2) + x,
                                                      (harf[1] - 19 + random.randint(-2 , 2)) + y, 0.3,
                                                      55 + random.randint(5, 15),
                                                      55 + random.randint(5, 15))
                                pyautogui.click(harf[0] + 30 + x + random.randint(-1 , 2), (harf[1] - 30) + y + random.randint(-2 , 1))
                                time.sleep(round(random.uniform(0.06, 0.15), 2))
                                pyautogui.click(harf[0] + 32 + x + random.randint(-1 , 2), (harf[1] - 32) + y + random.randint(-2 , 1))
                                time.sleep(random.uniform(0.2, 0.4))
                                human_like_mouse_move(random.randint(940, 1600),
                                                      random.randint(300, 800), 0.3,
                                                      55 + random.randint(5, 15),
                                                      55 + random.randint(5, 15))

                                time.sleep(0.65)

                                maptest = imagesearcharea(image_path("Harita.png"), 760, 146, 930, 270)

                                if maptest[0] != -1 and bolge != 0:
                                    found = False
                                    zaten_dovuste = imagesearcharea(image_path("iptal.png"), 182, 200, 1740, 863, 0.8)
                                    kapat = imagesearch(image_path("kapat.png"))

                                    if zaten_dovuste[0] != -1:
                                        print("Zaten dovuste")
                                        human_like_mouse_move(zaten_dovuste[0] + 182 + random.randint(-2, 2),
                                                              zaten_dovuste[1] + 200 + random.randint(-2, 2), 0.3,
                                                              55 + random.randint(5, 15),
                                                              55 + random.randint(5, 15))
                                        time.sleep(0.2)

                                        pyautogui.click(zaten_dovuste[0] + random.randint(1, 5) + 182,
                                                        zaten_dovuste[1] + 200 + random.randint(1, 5))
                                        found = False


                                    elif kapat[0] != -1:
                                        human_like_mouse_move(kapat[0],
                                                              kapat[1], 0.3,
                                                              55 + random.randint(5, 15),
                                                              55 + random.randint(5, 15))
                                        time.sleep(0.2)

                                        pyautogui.click(kapat[0] + random.randint(1, 5), kapat[1] + random.randint(1, 5))
                                        found = False


                            elif unlem[0] != -1:
                                print("Yaratık bulundu ama unlem var - SON")

                            elif found == False:
                                print("Yaratık tekrar arandı ama bulunamadı - SON")



                    else:
                        found = False
                        print("Yaratık bulundu ama unlem var")
                        time.sleep(0.14 + random.uniform(0.05, 0.1))
                        """human_like_mouse_move(avlan[0],
                                              avlan[1], 0.3,
                                              55 + random.randint(5, 15),
                                              55 + random.randint(5, 15))
                        time.sleep(0.14 + random.uniform(0.05, 0.1))
                        pyautogui.click(avlan[0], avlan[1])
                        time.sleep(1.5 + random.uniform(0.5, 1.0))"""
                        time.sleep(0.14 + random.uniform(0.05, 0.1))


                else:
                    found = False
                    print("Yaratık bulundu ama pixel fazla yukarıda")

            elif found==True:
                print("Ara süreç")
            else:
                found = False

            if found:
                sayac4 = 0
                time.sleep(0.05)
                bozuk = 0
                hizliaura = 0

                while True:
                    if sayac4 % 5 == 0:
                        print("Dovus ekranı bekleniyor")
                        if sayac4 % 30 == 0 and sayac4 != 0:
                            found = False
                            bozuk = 1
                            break
                    time.sleep(0.2)
                    golge = imagesearcharea(image_path("golge.png"), 244, 180, 700, 700)
                    if golge[0] != -1:
                        sayac4 = 0
                        break
                    sayac4 = sayac4 + 1


                time.sleep(0.05)
                iptal = imagesearch(image_path("iptal.png"))
                kapat = imagesearch(image_path("kapat.png"))
                olu_yaratık = imagesearch(image_path("harita.png"))

                if iptal[0] != -1:
                    human_like_mouse_move(iptal[0],
                                          iptal[1], 0.3,
                                          55 + random.randint(5, 15),
                                          55 + random.randint(5, 15))
                    time.sleep(0.2)

                    pyautogui.click(iptal[0]+random.randint(1,5), iptal[1]+random.randint(1,5))
                    found = False
                    bozuk = 1

                elif kapat[0] != -1:
                    human_like_mouse_move(kapat[0],
                                          kapat[1], 0.3,
                                          55 + random.randint(5, 15),
                                          55 + random.randint(5, 15))
                    time.sleep(0.2)

                    pyautogui.click(kapat[0]+random.randint(1,5), kapat[1]+random.randint(1,5))
                    found = False
                    bozuk = 1

                elif olu_yaratık[0] != -1:
                    time.sleep(1)
                    olu_yaratık = imagesearch(image_path("harita.png"))
                    if olu_yaratık[0] != -1:
                        human_like_mouse_move(avlan[0],
                                              avlan[1], 0.3,
                                              55 + random.randint(5, 15),
                                              55 + random.randint(5, 15))
                        time.sleep(0.2)

                        pyautogui.click(avlan[0]+random.randint(1,10), avlan[1]+random.randint(1,10))
                        found = False
                        bozuk = 1

                golge = imagesearcharea(image_path("golge.png"),244,180,307,246)
                aura = imagesearcharea(image_path("aura.png"),277,220,440,390)

                """BURAYIACif golge[0] != -1 and bozuk != 1 and aura[0] == -1:
                    aurahazirlik(kesim_control.get_troll_power_key(), kesim_control.get_aura_delay())
                    print("hizli aura basildi")
                    hizliaura = 1
                """
                time.sleep(0.1)
                while bozuk != 1:
                    Buyu = imagesearcharea(image_path("Buyu1.png"),400,300,600,600)
                    Buyu_2 = imagesearcharea(image_path("Buyu2.png"),400,300,600,500)
                    Vurus = imagesearcharea(image_path("Vurus12.png"),400,300,600,500)

                    if Buyu[0] == -1 and Vurus[0] == -1 and Buyu_2[0] == -1:
                        print("Sıra yaratıkta, beklemeye devam:", sayac1)
                        if sayac3 > 1 or (sayac1 % 10 == 0 and sayac1 != 0):
                            if zafer():
                                found = False
                                savas_sonu = 1
                                time.sleep(0.2)
                                savastan_cik(avlan,0)
                                print("savastan cikildi")
                                sayac = 0
                                sayac1 = 0
                                sayac2 = 0
                                sayac3 = 0
                                key_press_state = 0
                                kesilen_slot = kesilen_slot+1
                                print("Kesilen Slot : " , kesilen_slot)
                                kesim_control.update_kesilen_yaratik_count()  # Update the count
                                spammer.stop_spamming()
                                myiksir.aktiflik_sifirla()
                                time.sleep(0.5)
                                break
                        if sayac1 < 35:
                            spammer.stop_spamming()
                            time.sleep(0.03)
                            if sayac1 > 5 and sayac3 != 0:
                                time.sleep(0.2)
                            print("Bekleme sayaci" , sayac1)
                        if sayac1%7 == 0 and sayac1 != 0:
                            bozuk = 0
                            iptal =  imagesearch(image_path("iptal.png"))
                            kapat = imagesearch(image_path("kapat.png"))
                            if iptal[0] != -1:
                                human_like_mouse_move(iptal[0],
                                                      iptal[1], 0.3,
                                                      55 + random.randint(5, 15),
                                                      55 + random.randint(5, 15))
                                time.sleep(0.2)

                                pyautogui.click(iptal[0], iptal[1])
                                bozuk = 1
                                time.sleep(1)
                            if kapat[0] != -1:
                                human_like_mouse_move(kapat[0],
                                                      kapat[1], 0.3,
                                                      55 + random.randint(5, 15),
                                                      55 + random.randint(5, 15))
                                time.sleep(0.2)

                                pyautogui.click(kapat[0], kapat[1])
                                bozuk = 1
                                time.sleep(1)
                            if bozuk == 1:
                                bozuk = 0
                                sayac1=0
                                if(find_situation() == 0):
                                    found = True
                                else:
                                    found = False
                                break
                            time.sleep(0.3)
                        if sayac1 >= 35:
                            sayac1 = 0
                            sayac2 = 0
                            sayac3 = 0
                            key_press_state = 0
                            spammer.stop_spamming()
                            found=False
                            myiksir.aktiflik_sifirla()
                            break

                        sayac1 = sayac1 + 1

                    elif Buyu[0] != -1 or Vurus[0] != -1 or Buyu_2[0] != -1:
                        print("Vurus bulundu:", sayac1)
                        sayac1 = 0

                        if sayac3 == 0:
                            time.sleep(0.12 + random.uniform(-0.04, 0.01))
                            print("İlk tur can hesaplanmaz, yemeğe dikkat")
                            myiksir.iksir_ic(sayac3, 100,100,1,1)
                            time.sleep(0.05 + random.uniform(-0.01, 0.01))

                        if sayac3 > 2:
                            if health < 50:
                                time.sleep(0.05 + random.uniform(-0.01, 0.01))
                                health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                print("Mevcut can: %", health)
                                print("Rakip can: %", rakip_Can)
                                print("Mana: %", mana)
                                if sayi == 1:
                                    print("Rakip Sayisi 1")
                                else:
                                    print("Rakip Sayisi 1 den fazla")

                                myiksir.iksir_ic(sayac3, health, mana, sayi, 1)
                                time.sleep(0.15 + random.uniform(-0.01, 0.01))

                        sayac3 = sayac3 + 1
                        sayac2 = sayac2 + 1
                        print("Vurus sayisi: ", sayac3)


                        """BURAYIACif sayac3>1: #and sayac3 % 5 == 0:
                            buyutab = imagesearcharea(image_path("buyutab.png"),353,268,578,446)
                            if buyutab[0] != -1:
                                time.sleep(0.3)
                                buyutab = imagesearcharea(image_path("buyutab.png"), 353, 268, 578, 446)
                                if buyutab[0] != -1:
                                    time.sleep(0.3)
                                    buyutab = imagesearcharea(image_path("buyutab.png"), 353, 268, 578, 446)
                                    if buyutab[0] != -1:
                                        time.sleep(0.3)
                                        pyautogui.press('tab')
                                        print("BUYU TABI KAPANDI")

                        if sayac3>1: # and sayac3 % 5 == 0:
                            aura = imagesearcharea(image_path("aura.png"), 277, 220, 440, 390)
                            if aura[0] == -1:
                                time.sleep(0.3)
                                aura = imagesearcharea(image_path("aura.png"), 277, 220, 440, 390)
                                if aura[0] == -1:
                                    time.sleep(0.3)
                                    aura = imagesearcharea(image_path("aura.png"), 277, 220, 440, 390)
                                    if aura[0] == -1:
                                        health, rakip_Can, mana, sayi = calculateHealth_EnemyNumber()
                                        print("Mevcut can: %", health)
                                        print("Rakip can: %", rakip_Can)
                                        print("Mana: %", mana)
                                        if mana >= 40:
                                            pyautogui.press('t')
                                            print("AURA AÇILDI")
                                        elif mana < 40:
                                            print("AURA kapanmis ancak mana yetersiz")
                                else:
                                    print("Aura acik")
                            else:
                                print("Aura acik")
                        """



                        if tip == 1:

                            if sayac3 >= 2:
                                if sayac3 % 4 == 1 and kombinasyon[0] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 4 == 1 and kombinasyon[0] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 4 == 1 and kombinasyon[0] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 4 == 2 and kombinasyon[1] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 4 == 2 and kombinasyon[1] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 4 == 2 and kombinasyon[1] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 4 == 3 and kombinasyon[2] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 4 == 3 and kombinasyon[2] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 4 == 3 and kombinasyon[2] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 4 == 0 and kombinasyon[3] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 4 == 0 and kombinasyon[3] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 4 == 0 and kombinasyon[3] == "alt":
                                    spammer.start_spamming('e')


                            if sayac3 % 4 == 1:
                                if kombinasyon[0] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[0] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[0] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 4 == 2:
                                if kombinasyon[1] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[1] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[1] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 4 == 3:
                                if kombinasyon[2] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[2] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[2] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 4 == 0:
                                if kombinasyon[3] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[3] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[3] == "alt":
                                    pyautogui.press('e')

                            if sayac3 >= 2:
                                spammer.stop_spamming()

                        elif tip == 2:
                            if sayac3 >= 2:
                                if sayac3 % 5 == 1 and kombinasyon[0] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 5 == 1 and kombinasyon[0] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 5 == 1 and kombinasyon[0] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 5 == 2 and kombinasyon[1] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 5 == 2 and kombinasyon[1] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 5 == 2 and kombinasyon[1] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 5 == 3 and kombinasyon[2] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 5 == 3 and kombinasyon[2] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 5 == 3 and kombinasyon[2] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 5 == 4 and kombinasyon[3] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 5 == 4 and kombinasyon[3] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 5 == 4 and kombinasyon[3] == "alt":
                                    spammer.start_spamming('e')
                                elif sayac3 % 5 == 0 and kombinasyon[4] == "ust":
                                    spammer.start_spamming('q')
                                elif sayac3 % 5 == 0 and kombinasyon[4] == "duz":
                                    spammer.start_spamming('w')
                                elif sayac3 % 5 == 0 and kombinasyon[4] == "alt":
                                    spammer.start_spamming('e')

                            if sayac3 % 5 == 1:
                                if kombinasyon[0] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[0] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[0] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 5 == 2:
                                if kombinasyon[1] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[1] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[1] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 5 == 3:
                                if kombinasyon[2] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[2] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[2] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 5 == 4:
                                if kombinasyon[3] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[3] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[3] == "alt":
                                    pyautogui.press('e')

                            elif sayac3 % 5 == 0:
                                if kombinasyon[4] == "ust":
                                    pyautogui.press('q')
                                elif kombinasyon[4] == "duz":
                                    pyautogui.press('w')
                                elif kombinasyon[4] == "alt":
                                    pyautogui.press('e')

                            if sayac3 >= 2:
                                spammer.stop_spamming()


                        """
                        time.sleep(0.07)
                        if sayac3 >= 2:
                            if sayac3 % 4 == 0:
                                spammer.start_spamming('e')
                            else:
                                spammer.start_spamming('q')

                        if sayac3 == 1:
                            if hizliaura == 0:
                                aurahazirlik()
                            time.sleep(0.08 + random.uniform(-0.02, 0.02))
                            if sayac3 % 4 == 0 and sayac3 != 0:
                                pyautogui.press('e')
                            else:
                                pyautogui.press('q')
                            time.sleep(0.05 + random.uniform(-0.01, 0.01))

                        else:

                            time.sleep(0.05 + random.uniform(-0.01, 0.01))
                            if sayac3 % 4 == 0 and sayac3 != 0:
                                pyautogui.press('e')
                            else:
                                pyautogui.press('q')
                            time.sleep(0.04 + random.uniform(-0.01, 0.01))

                        time.sleep(0.05 + random.uniform(-0.01, 0.01))
                        if sayac3 >= 2:
                            spammer.stop_spamming()
                        """

                        time.sleep(0.7)

                        binek = imagesearcharea(image_path("Binek.png"),1558,155,2419,725,0.9)
                        print(binek)
                        if  binek[0] != -1:
                            found = False
                            savas_sonu = 1
                            time.sleep(0.1)
                            savastan_cik(avlan,1)
                            print("hizli cikis aktif")
                            sayac = 0
                            sayac1 = 0
                            sayac2 = 0
                            sayac3 = 0
                            key_press_state = 0
                            kesilen_slot = kesilen_slot + 1

                            yaratik_arasi_bekleme = random.randint(1,101)
                            if yaratik_arasi_bekleme % 50 ==0:
                                bekleme_süresi = yaratik_arasi_bekleme % 7 + 5
                                print("Kesim arasi bekleme aktif : " , bekleme_süresi , " saniye" )
                                time.sleep(bekleme_süresi)

                            print("Kesilen Slot : ", kesilen_slot)
                            kesim_control.update_kesilen_yaratik_count()  # Update the count
                            spammer.stop_spamming()
                            myiksir.aktiflik_sifirla()
                            time.sleep(0.5)
                            break

                        if (sayac3 != 0 or sayac3 == 1) :
                            if (sayac3 == 1 or health >= 50):
                                time.sleep(0.08 + random.uniform(-0.01, 0.01))
                                health,rakip_Can,mana,sayi = calculateHealth_EnemyNumber()
                                print("Mevcut can: %", health)
                                print("Rakip can: %", rakip_Can)
                                print("Mana: %", mana)
                                if sayi == 1:
                                    print("Rakip Sayisi 1")
                                else:
                                    print("Rakip Sayisi 1 den fazla")

                                myiksir.iksir_ic(sayac3,health,mana,sayi,1)
                                time.sleep(0.1 + random.uniform(-0.01, 0.01))

            if sayac < 20 and not found and savas_sonu == 0:
                print("Sayaca girdi", sayac)
                if sayac % 1 == 0: #sayac == 0 or
                    Map = imagesearch(image_path("Harita.png"))
                    #print(Map[0], Map[1])
                if Map[0] == -1:
                    time.sleep(0.5)
                    print("Avlan tabı bulunamadı. Birazdan avlana geri gecilecek.")
                    if find_situation() == 0:
                        found = True
                        sayac = 0
                    else:
                        found = False
                        sayac = sayac + 1
                        if sayac % 5 == 0 and sayac != 0:
                            human_like_mouse_move(avlan[0],
                                                  avlan[1], 0.3,
                                                  55 + random.randint(5, 15),
                                                  55 + random.randint(5, 15))
                            pyautogui.click(avlan)
                            time.sleep(2)
                elif Map[0] != -1 and  sayac < 20:
                    #pyautogui.click(945, 213 - randrange(0, 25))
                    random_arama_araci = random.randint(1,100)

                    if random_arama_araci % 5 == 0:
                        human_like_mouse_move(Map[0] + 75, Map[1] + random.randrange(-20, 11), 0.3,
                                              2 + random.randint(1, 4),
                                              2 + random.randint(1, 4))
                        pyautogui.click(Map[0] + 75, Map[1] + random.randrange(-20, 11))
                        time.sleep(1.2)
                    else:
                        if random_arama_araci % 2==0:
                            x_cord = 500 + random.randrange(10, 1100)
                            y_cord = 260 + random.randrange(10, 120)
                            human_like_mouse_move(x_cord,y_cord, 0.3,
                                                  2 + random.randint(1, 4),
                                                  2 + random.randint(1, 4))
                            time.sleep(random.uniform(0.01, 0.1))
                            pyautogui.mouseDown()
                            time.sleep(random.uniform(0.01, 0.1))
                            human_like_mouse_move(random.randint(random.randint(245, 245 + abs(245 - x_cord)) , random.randint(x_cord, x_cord + abs(1500 - x_cord))),
                                              random.randint(int(y_cord+(777-y_cord)*0.8), random.randint(int(y_cord+(777-y_cord)*0.8), 777)),
                                                  0.3,
                                              15 + random.randint(3, 6),
                                              15 + random.randint(3, 6))
                            time.sleep(random.uniform(0.01, 0.1))
                            pyautogui.mouseUp()
                            time.sleep(random.uniform(0.01, 0.1))

                        else:
                            x_cord = 500 + random.randrange(10, 1100)
                            y_cord = 700 + random.randrange(5, 40)
                            human_like_mouse_move(x_cord, y_cord, 0.3,
                                                  2 + random.randint(1, 4),
                                                  2 + random.randint(1, 4))
                            time.sleep(random.uniform(0.01, 0.1))
                            pyautogui.mouseDown()
                            time.sleep(random.uniform(0.01, 0.1))
                            human_like_mouse_move(random.randint(random.randint(245, 245 + abs(245 - x_cord)) , random.randint(x_cord, x_cord + abs(1500 - x_cord))),
                                              random.randint(250, random.randint(250,int(y_cord-(y_cord-250)/2))),
                                                  0.3,
                                              15 + random.randint(3, 6),
                                              15 + random.randint(3, 6))
                            time.sleep(random.uniform(0.01, 0.1))
                            pyautogui.mouseUp()
                            time.sleep(random.uniform(0.01, 0.1))


                    sayac = sayac + 1

            elif sayac >= 20 and not found:
                print("sayac < 20")
                time.sleep(1)
                if find_situation() == 0:
                    found = True
                else:
                    found = False
                    human_like_mouse_move(avlan[0],
                                          avlan[1], 0.3,
                                          55 + random.randint(5, 15),
                                          55 + random.randint(5, 15))
                    pyautogui.click(avlan[0], avlan[1])
                sayac = 0
                time.sleep(3)

    except Exception as e:
        input(e)  # Kullanıcı ENTER'a basana kadar bekler

    print("Main operation completed")
    kesim_control.temizle_temp_klasoru()

def toggle_log_frame():
    # Check if log_frame is packed (visible)
    if log_frame.winfo_manager():  # Returns the geometry manager method if the widget is managed
        log_frame.pack_forget()  # If visible, hide it
        toggle_button.config(text="Logları Göster")
    else:
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # If not visible, show it
        toggle_button.config(text="Logları Gizle")

if __name__ == "__main__":
    try:
        pyautogui.FAILSAFE = False
        freeze_support()
        print("Start")

        root = tk.Tk()
        root.title('HayaletV8')

        # Set fixed window size
        #root.geometry("400x900")
        root.resizable(False, False)

        # Apply a theme
        style = ttk.Style(root)
        style.theme_use('clam')  # You can choose 'clam', 'alt', 'default', 'classic'

        # Customize styles
        style.configure('TFrame', background='#e6f7ff')
        style.configure('TLabel', background='#e6f7ff', foreground='#333333', font=('Arial', 10))
        style.configure('TButton', background='#e6f7ff', foreground='#333333', font=('Arial', 10, 'bold'))
        style.configure('TNotebook', background='#e6f7ff')
        style.configure('TNotebook.Tab', background='#e6f7ff', foreground='#333333', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#99ccff'), ('active', '#b3d9ff')],
                  foreground=[('selected', '#333333')], expand=[('selected', [1, 1, 1, 0])])

        # Disable dotted focus ring on tabs
        style.layout('TNotebook.Tab', [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                    ('Notebook.label', {'side': 'top', 'sticky': ''})
                ]})
            ]})
        ])

        main_frame = tk.Frame(root, background="#e6f7ff")
        main_frame.pack(side=tk.LEFT)

        detay_frame = tk.Frame(main_frame, background="#e6f7ff")
        detay_frame.pack(side=tk.TOP)

        # Log section at the bottom
        log_frame = tk.Frame(main_frame, background="#ffffff")
        # Initially, let's pack it normally, or you could start with it hidden using log_frame.pack_forget()

        log_label = ttk.Label(log_frame, text="LOG KAYITLARI", background='#ffffff', style='LogLabel.TLabel')
        log_label.pack(pady=5)

        logs = tk.Text(log_frame, height=15, bg='#ffffff', fg='#333333', font=('Arial', 10), state=tk.DISABLED)
        logs.pack(fill=tk.BOTH, expand=True)
        logs.config(state=tk.NORMAL)
        logs.insert(tk.END, "Bot started.\n")
        logs.config(state=tk.DISABLED)

        # Toggle button to show/hide logs
        toggle_button = ttk.Button(main_frame, text="Logları Göster", command=toggle_log_frame)
        toggle_button.pack(side=tk.TOP, pady=10)

        kesim_control = ThreadControl(detay_frame, logs, main)
        myiksir = iksir(kesim_control)

        def on_closing():
            kesim_control.stop()
            if spammer.is_alive():  # Check if the spammer thread is alive before stopping
                spammer.stop_spamming()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        process_log_queue(log_queue, logs)

        root.mainloop()

    except Exception as e:
        input(e)  # Kullanıcı ENTER'a basana kadar bekler
