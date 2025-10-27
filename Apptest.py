import tkinter as tk
from tkinter import Canvas, NW
from PIL import Image, ImageTk
import webbrowser

# === Dictionnaire de couleurs ===
couleur = {
    "nero": "#252726",
    "purple": "#800080",
    "white": "#FFFFFF",
    "vertFonce": "#006400",   # Vert principal
    "vertClair": "#228B22"    # Vert clair
}

# === Couleur de fond principale ===
couleurFondImage = "#2E8B57"  # Vert doux

# === Fenêtre principale ===
app = tk.Tk()
app.title("Mon application")
app.config(bg=couleurFondImage)
app.geometry("500x500")

# === Icône (facultative) ===
try:
    app.iconbitmap("logo.ico")
except Exception as e:
    print("Icône non trouvée :", e)

# État du menu
btnEtat = False

# === Chargement des images ===
try:
    navIcon = ImageTk.PhotoImage(Image.open("menu.png").resize((25, 25)))
    closeIcon = ImageTk.PhotoImage(Image.open("Close.png").resize((25, 25)))
except Exception as e:
    print("⚠️ Problème de chargement image :", e)
    navIcon = closeIcon = None

# === Image de fond ===
try:
    bg_image_original = Image.open("back_image.png")
except Exception as e:
    print("⚠️ Impossible de charger l'image de fond :", e)
    bg_image_original = None

# === BARRE DU HAUT ===
topFrame = tk.Frame(app, bg=couleur["vertFonce"], height=50)
topFrame.pack(side="top", fill=tk.X)

# === BOUTON BURGER ===
navbarBtn = tk.Button(
    topFrame,
    image=navIcon,
    bg=couleur["vertFonce"],
    bd=0,
    padx=20,
    activebackground=couleur["vertClair"]
)
navbarBtn.place(x=10, y=10)

# === TITRE ===
accueilText = tk.Label(
    topFrame,
    text="JobFinder",
    font=("Arial", 15, "bold"),
    bg=couleur["vertFonce"],
    fg="white",
    height=2,
    padx=20
)
accueilText.pack(side="right")

# === CONTENU PRINCIPAL ===
mainFrame = tk.Frame(app, bg=couleurFondImage)
mainFrame.pack(fill="both", expand=True)

# --- Page d'accueil ---
def showAccueil():
    for widget in mainFrame.winfo_children():
        widget.destroy()

    # === Canvas pour l'image de fond ===
    canvas = Canvas(mainFrame, width=500, height=500, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # --- Fonction pour redimensionner l’image selon la taille de la fenêtre ---
    def resize_bg(event):
        if bg_image_original:
            new_width = event.width
            new_height = event.height
            resized = bg_image_original.resize((new_width, new_height + 80))  # ⬆️ Image légèrement remontée
            bg_photo = ImageTk.PhotoImage(resized)
            canvas.bg_photo = bg_photo  # garde la référence
            canvas.create_image(0, -40, image=bg_photo, anchor=NW)  # ⬆️ remonte légèrement l'image

    canvas.bind("<Configure>", resize_bg)

    # --- "Bouton" Commencer en Label cliquable ---
    btnStart = tk.Label(
        canvas,
        text="Commencer",
        font=("Arial", 14, "bold"),
        bg=couleurFondImage,  # couleur identique au canvas
        fg="white",
        cursor="hand2",
        padx=25,
        pady=10
    )
    btnStart.place(relx=0.5, rely=0.75, anchor="center")
    btnStart.bind("<Button-1>", lambda e: goOffres())

    # --- Lien “Se connecter” ---
    lienLogin = tk.Label(
        canvas,
        text="Déjà un compte ? Se connecter",
        font=("Arial", 11, "underline"),
        bg=couleurFondImage,  # couleur identique au canvas
        fg="white",
        cursor="hand2"
    )
    lienLogin.place(relx=0.5, rely=0.85, anchor="center")
    lienLogin.bind("<Button-1>", lambda e: goProfil())

# --- Page Contact ---
def showContact():
    for widget in mainFrame.winfo_children():
        widget.destroy()

    tk.Label(
        mainFrame,
        text="Contactez-nous",
        font=("Arial", 18, "bold"),
        bg=couleurFondImage,
        fg="white"
    ).pack(pady=30)

    contact_info = [
        ("📞 Téléphone :", "+212612345678", "tel:+212612345678"),
        ("✉️ Email :", "contact@jobfinder.ma", "mailto:contact@jobfinder.ma"),
        ("📍 Adresse :", "Oujda, Maroc", None),
        ("🌐 Site web :", "www.jobfinder.ma", "https://www.jobfinder.ma")
    ]

    for titre, valeur, lien in contact_info:
        label = tk.Label(
            mainFrame,
            text=f"{titre} {valeur}",
            font=("Arial", 13),
            bg=couleurFondImage,
            fg="white",
            anchor="w",
            cursor="hand2" if lien else "arrow"
        )
        label.pack(pady=8, padx=20, anchor="w")
        if lien:
            label.bind("<Button-1>", lambda e, url=lien: webbrowser.open(url))

# === NAVBAR LATÉRALE ===
navLateral = tk.Frame(app, bg="#013220", width=300, height=600)
navLateral.place(x=-300, y=0)

tk.Label(
    navLateral,
    text="MENU",
    font=("Arial", 15, "bold"),
    bg=couleur["vertFonce"],
    fg="white",
    width=300,
    height=2
).place(x=0, y=0)

# === FONCTIONS DES PAGES ===
def goAccueil():
    toggleMenu()
    showAccueil()

def goProfil():
    toggleMenu()
    for widget in mainFrame.winfo_children():
        widget.destroy()
    tk.Label(
        mainFrame,
        text="Profil utilisateur",
        font=("Arial", 18, "bold"),
        bg=couleurFondImage,
        fg="white"
    ).pack(pady=50)

def goOffres():
    toggleMenu()
    for widget in mainFrame.winfo_children():
        widget.destroy()
    tk.Label(
        mainFrame,
        text="Offres d'emploi disponibles",
        font=("Arial", 16, "bold"),
        bg=couleurFondImage,
        fg="white"
    ).pack(pady=50)

def goParametres():
    toggleMenu()
    for widget in mainFrame.winfo_children():
        widget.destroy()
    tk.Label(
        mainFrame,
        text="Paramètres de l'application",
        font=("Arial", 16, "bold"),
        bg=couleurFondImage,
        fg="white"
    ).pack(pady=50)

def goContact():
    toggleMenu()
    showContact()

# === BOUTONS DU MENU ===
menu_buttons = [
    ("Accueil", goAccueil),
    ("Profil", goProfil),
    ("Offres d'emploi", goOffres),
    ("Paramètres", goParametres),
    ("Contact", goContact)
]

y = 80
for text, cmd in menu_buttons:
    tk.Button(
        navLateral,
        text=text,
        font=("Arial", 13, "bold"),
        bg="#013220",
        fg=couleur["white"],
        activebackground="#1b4d2b",
        bd=0,
        command=cmd
    ).place(x=25, y=y)
    y += 40

# === FONCTION POUR LE MENU BURGER ===
def toggleMenu():
    global btnEtat
    if btnEtat:
        for x in range(0, 301, 10):
            navLateral.place(x=-x, y=0)
            app.update()
        navLateral.place(x=-300, y=0)
        navbarBtn.config(image=navIcon)
        btnEtat = False
    else:
        for x in range(-300, 1, 10):
            navLateral.place(x=x, y=0)
            app.update()
        navLateral.place(x=0, y=0)
        topFrame.tkraise()
        navbarBtn.config(image=closeIcon)
        btnEtat = True

navbarBtn.config(command=toggleMenu)

# === PAGE PAR DÉFAUT ===
showAccueil()

# === BOUCLE PRINCIPALE ===
app.mainloop()
