import customtkinter
import pygame
from tkinter import filedialog
import requests
import threading

pygame.mixer.init()

app = customtkinter.CTk()
app.title("Dashboard")
app.geometry("1050x500")
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

#les petites couleuurss
BG     = "#1A1A2E"
CARD   = "#16213E"
ACCENT = "#0F3460"
BLUE   = "#4A90D9"
GREEN  = "#4CAF50"
ORANGE = "#E07B39"
RED    = "#E05252"
WHITE  = "#E8E8E8"
GREY   = "#888888"

app.configure(fg_color=BG)

for i in range(4):
    app.columnconfigure(i, weight=1)
app.rowconfigure(0, weight=1)

def card_frame(col):
    f = customtkinter.CTkFrame(app, fg_color=CARD, corner_radius=14)
    f.grid(row=0, column=col, padx=10, pady=16, sticky="nsew")
    return f

def title_label(parent, text, color=BLUE):
    customtkinter.CTkLabel(parent, text=text,
                           font=customtkinter.CTkFont(size=13, weight="bold"),
                           text_color=color).pack(pady=(14, 4))
    customtkinter.CTkFrame(parent, height=1, fg_color=ACCENT).pack(fill="x", padx=14, pady=(0, 8))

# METEOOO----------
meteo_card = card_frame(0)
title_label(meteo_card, "Météo — Rouen")

temp_lbl = customtkinter.CTkLabel(meteo_card, text="--°C",
                                   font=customtkinter.CTkFont(size=32, weight="bold"),
                                   text_color=BLUE)
temp_lbl.pack()
desc_lbl = customtkinter.CTkLabel(meteo_card, text="", text_color=WHITE,
                                   font=customtkinter.CTkFont(size=11))
desc_lbl.pack(pady=2)
hum_lbl  = customtkinter.CTkLabel(meteo_card, text="", text_color=GREY,
                                   font=customtkinter.CTkFont(size=10))
hum_lbl.pack()
vent_lbl = customtkinter.CTkLabel(meteo_card, text="", text_color=GREY,
                                   font=customtkinter.CTkFont(size=10))
vent_lbl.pack()

customtkinter.CTkFrame(meteo_card, height=1, fg_color=ACCENT).pack(fill="x", padx=14, pady=(10, 6))
customtkinter.CTkLabel(meteo_card, text="Tenue conseillée",
                        font=customtkinter.CTkFont(size=11, weight="bold"),
                        text_color=ORANGE).pack()
conseil_lbl = customtkinter.CTkLabel(meteo_card, text="", text_color=WHITE,
                                      font=customtkinter.CTkFont(size=10),
                                      wraplength=200, justify="left")
conseil_lbl.pack(pady=(4, 10), padx=12)

def clothing(temp, desc, wind):
    d = desc.lower()
    lines = []
    if temp < 0:      lines += ["Manteau long, gants, bonnet", "Bottes imperméables"]
    elif temp < 8:    lines += ["Manteau chaud + écharpe", "Pantalon épais"]
    elif temp < 15:   lines += ["Veste + pull", "Pantalon long"]
    elif temp < 20:   lines += ["Sweat léger", "Jean"]
    elif temp < 26:   lines += ["T-shirt / chemise", "Jean léger"]
    else:             lines += ["Short + t-shirt", "Crème solaire"]
    if any(x in d for x in ["rain","drizzle","pluie"]): lines.append("Parapluie")
    if any(x in d for x in ["snow","neige"]):           lines.append("Bottes, imperméable")
    if wind > 10:                                        lines.append("Coupe-vent")
    return "\n".join(lines[:3])

def load_weather():
    try:
        url = "http://api.openweathermap.org/data/2.5/weather?lat=49.4333&lon=1.0833&appid=9dd7f7285fa06d00101e3daa33580967&lang=fr"
        data = requests.get(url, timeout=8).json()
        tc   = data["main"]["temp"] - 273.15
        desc = data["weather"][0]["description"].capitalize()
        hum  = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        temp_lbl.configure(text=f"{tc:.0f}°C",
                            text_color="#60A5FA" if tc < 10 else GREEN if tc < 22 else ORANGE)
        desc_lbl.configure(text=desc)
        hum_lbl.configure(text=f"Humidité : {hum}%")
        vent_lbl.configure(text=f"Vent : {wind} m/s")
        conseil_lbl.configure(text=clothing(tc, desc, wind))
    except:
        desc_lbl.configure(text="Erreur réseau", text_color=RED)

threading.Thread(target=load_weather, daemon=True).start()
customtkinter.CTkButton(meteo_card, text="Actualiser", height=26,
                         fg_color=ACCENT, hover_color="#1a4a7a",
                         command=lambda: threading.Thread(target=load_weather, daemon=True).start()
                         ).pack(pady=(0, 14))

# MUSIQUE---
music_card = card_frame(1)
title_label(music_card, "Musique", color="#A78BFA")

track_lbl = customtkinter.CTkLabel(music_card, text="Aucune piste", text_color=GREY,
                                    font=customtkinter.CTkFont(size=10), wraplength=180)
track_lbl.pack(pady=(0, 8))

_paused = {"v": False}
_pp_btn = None

def load_music():
    import os
    fp = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3 *.wav *.ogg")])
    if not fp: return
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    track_lbl.configure(text=os.path.basename(fp)[:28])
    _paused["v"] = False
    _pp_btn.configure(text="Pause")

def toggle_pp():
    if _paused["v"]:
        pygame.mixer.music.unpause(); _paused["v"] = False; _pp_btn.configure(text="Pause")
    else:
        pygame.mixer.music.pause();   _paused["v"] = True;  _pp_btn.configure(text="Lecture")

def mk_btn(parent, text, cmd, color=ACCENT):
    return customtkinter.CTkButton(parent, text=text, command=cmd,
                                   fg_color=color, hover_color="#1a4a7a",
                                   height=30, corner_radius=8,
                                   font=customtkinter.CTkFont(size=11))

mk_btn(music_card, "Ouvrir", load_music).pack(fill="x", padx=16, pady=3)
_pp_btn = mk_btn(music_card, "Lecture", toggle_pp)
_pp_btn.pack(fill="x", padx=16, pady=3)
mk_btn(music_card, "Stop", lambda: pygame.mixer.music.stop()).pack(fill="x", padx=16, pady=3)

customtkinter.CTkLabel(music_card, text="Volume", text_color=GREY,
                        font=customtkinter.CTkFont(size=10)).pack(pady=(10, 0))
vol = customtkinter.CTkSlider(music_card, from_=0, to=1,
                               progress_color="#A78BFA", button_color="#A78BFA")
vol.set(0.8)
vol.pack(padx=16, pady=(2, 14))
vol.configure(command=lambda v: pygame.mixer.music.set_volume(float(v)))
pygame.mixer.music.set_volume(0.8)

#NOTES---------
note_card = card_frame(2)
title_label(note_card, "Notes", color=ORANGE)

tab_n = {"n": 1}
tabs = customtkinter.CTkTabview(note_card, fg_color=ACCENT, corner_radius=8,
                                 segmented_button_fg_color=ACCENT,
                                 segmented_button_selected_color=BLUE)
tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

def add_note():
    name = f"Note {tab_n['n']}"
    tabs.add(name)
    customtkinter.CTkTextbox(tabs.tab(name), fg_color="#0d1b2e",
                              text_color=WHITE, font=customtkinter.CTkFont(size=11),
                              border_width=0).pack(fill="both", expand=True, pady=4)
    customtkinter.CTkButton(tabs.tab(name), text="+ Note", height=24,
                             fg_color=ACCENT, command=add_note,
                             font=customtkinter.CTkFont(size=10)).pack(pady=(2, 4))
    tab_n["n"] += 1

add_note()

#TACHES-A-FAURE------
title_label(todo_card, "Tâches", color=GREEN)

entry_row = customtkinter.CTkFrame(todo_card, fg_color="transparent")
entry_row.pack(fill="x", padx=10, pady=(0, 6))
entry_row.columnconfigure(0, weight=1)

task_entry = customtkinter.CTkEntry(entry_row, placeholder_text="Nouvelle tâche…",
                                     fg_color=ACCENT, border_color=BLUE,
                                     text_color=WHITE, font=customtkinter.CTkFont(size=11),
                                     height=30, corner_radius=6)
task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

customtkinter.CTkButton(entry_row, text="+", width=30, height=30,
                         fg_color=GREEN, hover_color="#3a8f3a",
                         text_color=BG, font=customtkinter.CTkFont(size=16, weight="bold"),
                         corner_radius=6, command=lambda: _add()
                         ).grid(row=0, column=1)

tasks_scroll = customtkinter.CTkScrollableFrame(todo_card, fg_color="transparent",
                                                 scrollbar_button_color=ACCENT)
tasks_scroll.pack(fill="both", expand=True, padx=10)
tasks_scroll.columnconfigure(0, weight=1)

count_lbl = customtkinter.CTkLabel(todo_card, text="", text_color=GREY,
                                    font=customtkinter.CTkFont(size=10))
count_lbl.pack(pady=(2, 10))

_tasks = []

def _stats():
    done = sum(1 for _, v in _tasks if v.get())
    count_lbl.configure(text=f"{done}/{len(_tasks)} faite{'s' if done != 1 else ''}")

def _add(event=None):
    text = task_entry.get().strip()
    if not text: return
    task_entry.delete(0, "end")
    row = customtkinter.CTkFrame(tasks_scroll, fg_color=ACCENT, corner_radius=6)
    row.pack(fill="x", pady=2)
    row.columnconfigure(1, weight=1)
    var = customtkinter.BooleanVar()
    _tasks.append((row, var))

    def on_check(r=row, v=var):
        for w in r.winfo_children():
            if isinstance(w, customtkinter.CTkLabel):
                w.configure(text_color=GREY if v.get() else WHITE)
        _stats()

    def on_delete(r=row, v=var):
        idx = next((i for i, (x, _) in enumerate(_tasks) if x == r), None)
        if idx is not None: _tasks.pop(idx)
        r.destroy()
        _stats()

    customtkinter.CTkCheckBox(row, text="", variable=var, fg_color=GREEN,
                               hover_color="#3a8f3a", checkmark_color=BG, width=16,
                               command=on_check).grid(row=0, column=0, padx=6, pady=6)
    customtkinter.CTkLabel(row, text=text, font=customtkinter.CTkFont(size=11),
                            text_color=WHITE, anchor="w").grid(row=0, column=1, sticky="ew")
    customtkinter.CTkButton(row, text="×", width=22, height=22,
                             fg_color="transparent", hover_color=RED,
                             text_color=GREY, corner_radius=4,
                             font=customtkinter.CTkFont(size=12),
                             command=on_delete).grid(row=0, column=2, padx=4)
    _stats()

task_entry.bind("<Return>", _add)

app.mainloop()