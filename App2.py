import tkinter as tk
from tkinter import Canvas, NW
from PIL import Image, ImageTk
import webbrowser
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

# === Dictionnaire de couleurs ===
couleur = {
    "nero": "#252726",
    "purple": "#800080",
    "white": "#FFFFFF"
}

# === Couleur de fond identique à l'image ===
couleurFondImage = "#00AEEF"  # bleu clair

# === Fenêtre principale ===
app = tk.Tk()
app.title("Mon application")
app.config(bg=couleurFondImage)
app.geometry("400x600")

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

# === BARRE DU HAUT ===
topFrame = tk.Frame(app, bg="#0d47a1", height=50)
topFrame.pack(side="top", fill=tk.X)

# === BOUTON BURGER ===
navbarBtn = tk.Button(
    topFrame,
    image=navIcon,
    bg="#0d47a1",
    bd=0,
    padx=20,
    activebackground="#1565c0"
)
navbarBtn.place(x=10, y=10)

# === TITRE ===
accueilText = tk.Label(
    topFrame,
    text="JobFinder",
    font=("Arial", 15, "bold"),
    bg="#0d47a1",
    fg="white",
    height=2,
    padx=20
)
accueilText.pack(side="right")

# === CONTENU PRINCIPAL ===
mainFrame = tk.Frame(app, bg=couleurFondImage)
mainFrame.pack(fill="both", expand=True)

# === Connexion MySQL et création table ===
def connexion_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",  # ton mot de passe MySQL
            database="jobfinder"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print("Erreur MySQL:", e)
        return None

def creer_base_et_table():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="")
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS jobfinder")
        cursor.execute("USE jobfinder")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                mot_de_passe VARCHAR(100)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print("Erreur création base/table:", e)

creer_base_et_table()

# Variable globale pour stocker l'utilisateur connecté
current_user = None

# Ajouter un utilisateur
def ajouter_utilisateur(nom, email, mdp):
    conn = connexion_mysql()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO utilisateurs (nom,email,mot_de_passe) VALUES (%s,%s,%s)",
                (nom,email,mdp)
            )
            conn.commit()
            messagebox.showinfo("Succès", f"Utilisateur {nom} ajouté!")
            cursor.execute("SELECT nom,email FROM utilisateurs WHERE email=%s", (email,))
            utilisateur = cursor.fetchone()
            global current_user
            current_user = utilisateur
            goProfil()  # afficher le profil directement après inscription
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erreur", "Email déjà utilisé!")
        finally:
            cursor.close()
            conn.close()

# --- Page d'inscription ---
def showInscription():
    for widget in mainFrame.winfo_children():
        widget.destroy()

    tk.Label(mainFrame, text="Inscription", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=20)

    tk.Label(mainFrame, text="Nom :", bg=couleurFondImage, fg="white").pack()
    entryNom = tk.Entry(mainFrame)
    entryNom.pack()

    tk.Label(mainFrame, text="Email :", bg=couleurFondImage, fg="white").pack()
    entryEmail = tk.Entry(mainFrame)
    entryEmail.pack()

    tk.Label(mainFrame, text="Mot de passe :", bg=couleurFondImage, fg="white").pack()
    entryMDP = tk.Entry(mainFrame, show="*")
    entryMDP.pack()

    tk.Button(mainFrame, text="S'inscrire", bg="#0d47a1", fg="white",
              command=lambda: ajouter_utilisateur(entryNom.get(), entryEmail.get(), entryMDP.get())).pack(pady=10)

# --- Page d'accueil ---
def showAccueil():
    for widget in mainFrame.winfo_children():
        widget.destroy()

    titre = tk.Label(
        mainFrame,
        text="Commençons à construire votre carrière",
        font=("Arial", 16, "bold"),
        bg=couleurFondImage,
        fg="white",
        wraplength=320,
        justify="center"
    )
    titre.place(relx=0.5, rely=0.35, anchor="center")

    desc = tk.Label(
        mainFrame,
        text="Découvrez de nouvelles opportunités et trouvez le métier de vos rêves dès aujourd’hui.",
        font=("Arial", 11),
        bg=couleurFondImage,
        fg="white",
        wraplength=320,
        justify="center"
    )
    desc.place(relx=0.5, rely=0.45, anchor="center")

    btnStart = tk.Button(
        mainFrame,
        text="Commencer",
        font=("Arial", 13, "bold"),
        bg="#0d47a1",
        fg="white",
        activebackground="#1565c0",
        activeforeground="white",
        relief="flat",
        padx=20,
        pady=8,
        command=goOffres
    )
    btnStart.place(relx=0.5, rely=0.55, anchor="center")

    # Lien "Se connecter"
    lienLogin = tk.Label(
        mainFrame,
        text="Déjà un compte ? Se connecter",
        font=("Arial", 11, "underline"),
        bg=couleurFondImage,
        fg="white",
        cursor="hand2"
    )
    lienLogin.place(relx=0.5, rely=0.65, anchor="center")
    lienLogin.bind("<Button-1>", lambda e: goProfil())

    # Lien "S'inscrire"
    lienInscription = tk.Label(
        mainFrame,
        text="Pas de compte ? S'inscrire",
        font=("Arial", 11, "underline"),
        bg=couleurFondImage,
        fg="white",
        cursor="hand2"
    )
    lienInscription.place(relx=0.5, rely=0.70, anchor="center")
    lienInscription.bind("<Button-1>", lambda e: showInscription())

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
navLateral = tk.Frame(app, bg="gray30", width=300, height=600)
navLateral.place(x=-300, y=0)

tk.Label(
    navLateral,
    text="MENU",
    font=("Arial", 15, "bold"),
    bg="#0d47a1",
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
    
    if current_user:
        nom, email = current_user
        tk.Label(mainFrame, text="Profil utilisateur", font=("Arial", 18, "bold"),
                 bg=couleurFondImage, fg="white").pack(pady=50)
        tk.Label(mainFrame, text=f"Nom : {nom}", font=("Arial", 14),
                 bg=couleurFondImage, fg="white").pack(pady=5)
        tk.Label(mainFrame, text=f"Email : {email}", font=("Arial", 14),
                 bg=couleurFondImage, fg="white").pack(pady=5)
    else:
        tk.Label(mainFrame, text="Aucun utilisateur connecté", font=("Arial", 14),
                 bg=couleurFondImage, fg="white").pack(pady=50)
        tk.Button(mainFrame, text="S'inscrire", bg="#0d47a1", fg="white",
                  command=showInscription).pack(pady=10)

def goOffres():
    toggleMenu()
    for widget in mainFrame.winfo_children():
        widget.destroy()
    tk.Label(mainFrame, text="Offres d'emploi disponibles", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=50)

def goParametres():
    toggleMenu()
    for widget in mainFrame.winfo_children():
        widget.destroy()
    tk.Label(mainFrame, text="Paramètres de l'application", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=50)

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
        bg="gray30",
        fg=couleur["white"],
        activebackground="#333333",
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
