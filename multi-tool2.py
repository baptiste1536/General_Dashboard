import customtkinter as ctk
import pygame
from tkinter import filedialog
import requests
import threading
import os

pygame.mixer.init()

# --- fenêtre ---
app = ctk.CTk()
app.title("Dashboard")
app.geometry("1050x500")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# couleurs
FOND = "#1A1A2E"
CARTE = "#16213E"
ACCENT = "#0F3460"
BLEU = "#4A90D9"
VERT = "#4CAF50"
ORANGE = "#E07B39"
ROUGE = "#E05252"
BLANC = "#E8E8E8"
GRIS = "#888888"

app.configure(fg_color=FOND)

for i in range(4):
    app.columnconfigure(i, weight=1)
app.rowconfigure(0, weight=1)


# --- helpers UI ---
def creer_carte(colonne):
    cadre = ctk.CTkFrame(app, fg_color=CARTE, corner_radius=14)
    cadre.grid(row=0, column=colonne, padx=10, pady=16, sticky="nsew")
    return cadre


def ajouter_titre(parent, texte, couleur=BLEU):
    ctk.CTkLabel(
        parent,
        text=texte,
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=couleur
    ).pack(pady=(14, 4))

    ctk.CTkFrame(parent, height=1, fg_color=ACCENT)\
        .pack(fill="x", padx=14, pady=(0, 8))


# =========================
# METEO
# =========================
carte_meteo = creer_carte(0)
ajouter_titre(carte_meteo, "Météo — Rouen")

label_temp = ctk.CTkLabel(carte_meteo, text="--°C",
                          font=ctk.CTkFont(size=32, weight="bold"))
label_temp.pack()

label_desc = ctk.CTkLabel(carte_meteo, text="", text_color=BLANC)
label_desc.pack(pady=2)

label_hum = ctk.CTkLabel(carte_meteo, text="", text_color=GRIS)
label_hum.pack()

label_vent = ctk.CTkLabel(carte_meteo, text="", text_color=GRIS)
label_vent.pack()

ctk.CTkFrame(carte_meteo, height=1, fg_color=ACCENT)\
    .pack(fill="x", padx=14, pady=(10, 6))

ctk.CTkLabel(carte_meteo, text="Tenue conseillée",
             text_color=ORANGE,
             font=ctk.CTkFont(size=11, weight="bold")).pack()

label_conseil = ctk.CTkLabel(
    carte_meteo,
    text="",
    wraplength=200,
    justify="left",
    text_color=BLANC
)
label_conseil.pack(pady=(4, 10), padx=12)


def tenue(temp, description, vent):
    d = description.lower()
    res = []

    if temp < 0:
        res += ["Manteau long, gants", "Bottes"]
    elif temp < 10:
        res += ["Manteau + écharpe"]
    elif temp < 18:
        res += ["Veste"]
    elif temp < 25:
        res += ["T-shirt"]
    else:
        res += ["Short", "Crème solaire"]

    if "pluie" in d or "rain" in d:
        res.append("Parapluie")
    if "neige" in d:
        res.append("Imperméable")
    if vent > 10:
        res.append("Coupe-vent")

    return "\n".join(res[:3])


def maj_meteo():
    try:
        url = "http://api.openweathermap.org/data/2.5/weather?lat=49.4333&lon=1.0833&appid=9dd7f7285fa06d00101e3daa33580967&lang=fr"
        data = requests.get(url, timeout=8).json()

        t = data["main"]["temp"] - 273.15
        desc = data["weather"][0]["description"].capitalize()

        label_temp.configure(
            text=f"{t:.0f}°C",
            text_color=BLEU if t < 10 else VERT if t < 22 else ORANGE
        )

        label_desc.configure(text=desc)
        label_hum.configure(text=f"Humidité : {data['main']['humidity']}%")
        label_vent.configure(text=f"Vent : {data['wind']['speed']} m/s")
        label_conseil.configure(text=tenue(t, desc, data["wind"]["speed"]))

    except Exception:
        label_desc.configure(text="Erreur réseau", text_color=ROUGE)


threading.Thread(target=maj_meteo, daemon=True).start()

ctk.CTkButton(
    carte_meteo,
    text="Actualiser",
    command=lambda: threading.Thread(target=maj_meteo, daemon=True).start()
).pack(pady=(0, 14))


# =========================
# MUSIQUE
# =========================
carte_musique = creer_carte(1)
ajouter_titre(carte_musique, "Musique", couleur="#A78BFA")

label_piste = ctk.CTkLabel(carte_musique, text="Aucune piste", text_color=GRIS)
label_piste.pack(pady=(0, 8))

en_pause = False


def ouvrir_fichier():
    global en_pause
    chemin = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3 *.wav *.ogg")])
    if not chemin:
        return

    pygame.mixer.music.load(chemin)
    pygame.mixer.music.play()

    label_piste.configure(text=os.path.basename(chemin)[:28])
    en_pause = False
    bouton_play.configure(text="Pause")


def toggle_lecture():
    global en_pause
    if en_pause:
        pygame.mixer.music.unpause()
        bouton_play.configure(text="Pause")
    else:
        pygame.mixer.music.pause()
        bouton_play.configure(text="Lecture")
    en_pause = not en_pause


def bouton(parent, texte, commande):
    return ctk.CTkButton(parent, text=texte, command=commande, height=30)


bouton(carte_musique, "Ouvrir", ouvrir_fichier).pack(fill="x", padx=16, pady=3)

bouton_play = bouton(carte_musique, "Lecture", toggle_lecture)
bouton_play.pack(fill="x", padx=16, pady=3)

bouton(carte_musique, "Stop", pygame.mixer.music.stop)\
    .pack(fill="x", padx=16, pady=3)

slider_volume = ctk.CTkSlider(carte_musique, from_=0, to=1)
slider_volume.set(0.8)
slider_volume.pack(padx=16, pady=10)

slider_volume.configure(command=lambda v: pygame.mixer.music.set_volume(float(v)))
pygame.mixer.music.set_volume(0.8)


# =========================
# NOTES
# =========================
carte_notes = creer_carte(2)
ajouter_titre(carte_notes, "Notes", couleur=ORANGE)

onglets = ctk.CTkTabview(carte_notes)
onglets.pack(fill="both", expand=True, padx=10, pady=(0, 10))

compteur_notes = 1


def nouvelle_note():
    global compteur_notes
    nom = f"Note {compteur_notes}"
    onglets.add(nom)

    zone = ctk.CTkTextbox(onglets.tab(nom))
    zone.pack(fill="both", expand=True)

    ctk.CTkButton(onglets.tab(nom), text="+ Note", command=nouvelle_note)\
        .pack(pady=4)

    compteur_notes += 1


nouvelle_note()


# =========================
# TODO LIST
# =========================
carte_taches = creer_carte(3)
ajouter_titre(carte_taches, "Tâches", couleur=VERT)

entree = ctk.CTkEntry(carte_taches, placeholder_text="Nouvelle tâche…")
entree.pack(fill="x", padx=10, pady=5)

zone_taches = ctk.CTkScrollableFrame(carte_taches)
zone_taches.pack(fill="both", expand=True, padx=10)

liste_taches = []


def maj_compteur():
    faites = sum(v.get() for _, v in liste_taches)
    label_compteur.configure(text=f"{faites}/{len(liste_taches)} faites")


def ajouter_tache(event=None):
    texte = entree.get().strip()
    if not texte:
        return

    entree.delete(0, "end")

    ligne = ctk.CTkFrame(zone_taches)
    ligne.pack(fill="x", pady=2)

    var = ctk.BooleanVar()
    liste_taches.append((ligne, var))

    def toggle():
        maj_compteur()

    def supprimer():
        liste_taches.remove((ligne, var))
        ligne.destroy()
        maj_compteur()

    ctk.CTkCheckBox(ligne, text="", variable=var,
                    command=toggle).pack(side="left")

    ctk.CTkLabel(ligne, text=texte)\
        .pack(side="left", fill="x", expand=True)

    ctk.CTkButton(ligne, text="×", width=22,
                  command=supprimer).pack(side="right")

    maj_compteur()


entree.bind("<Return>", ajouter_tache)

ctk.CTkButton(carte_taches, text="+", command=ajouter_tache).pack(pady=4)

label_compteur = ctk.CTkLabel(carte_taches, text="", text_color=GRIS)
label_compteur.pack(pady=5)


# --- lancement ---
app.mainloop()
