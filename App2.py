# App2.py - version corrigée (conserve ta structure originale, corrige bugs)
import tkinter as tk
from tkinter import Canvas, NW
from PIL import Image, ImageTk
import webbrowser
from tkinter import messagebox, Toplevel, Label, Entry, Text, Button
import mysql.connector
from mysql.connector import Error
import bcrypt

# -----------------------------
# Variables globales
# -----------------------------
current_user = None
current_user_role = None

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
    app.iconbitmap("sahar.ico")
except Exception as e:
    print("Icône non trouvée :", e)

# État du menu
btnEtat = False

# === Chargement des images ===
try:
    navIcon = ImageTk.PhotoImage(Image.open("menu.png").resize((25, 25)))
    closeIcon = ImageTk.PhotoImage(Image.open("close.png").resize((25, 25)))
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

# -----------------------------
# MySQL connexion
# -----------------------------
def connexion_mysql():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="admin_py",
            password="admin",  # adapte ton mot de passe
            database="projet"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print("Erreur MySQL:", e)
        return None

def creer_base_et_table():
    try:
        conn = connexion_mysql()
        if not conn:
            return
        cursor = conn.cursor()
        # Tu as commenté la création — je laisse telle quelle
        # Si tu veux créer la table depuis le script, décommente et adapte
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS utilisateurs (
        #         id INT AUTO_INCREMENT PRIMARY KEY,
        #         nom VARCHAR(100),
        #         email VARCHAR(100) UNIQUE,
        #         mot_de_passe BLOB,
        #         role ENUM('admin','rh','chercheur','user') DEFAULT 'user'
        #     )
        # """)
       # cursor.execute("""  CREATE TABLE IF NOT EXISTS offres (
        #id INT AUTO_INCREMENT PRIMARY KEY,
        #titre VARCHAR(150),
        #description TEXT,
        #lieu VARCHAR(100),
        #salaire VARCHAR(50),
        #type VARCHAR(50),
         #date_publication DATETIME DEFAULT CURRENT_TIMESTAMP
        #)""")

        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print("Erreur création base/table:", e)

# -----------------------------
# BCrypt helpers
# -----------------------------
def hash_password(plain_password: str) -> bytes:
    """Retourne hash bcrypt (bytes)."""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

def is_bcrypt_hash(value) -> bool:
    """Vérifie si value (bytes/str/memoryview) ressemble à un hash bcrypt."""
    if value is None:
        return False
    if isinstance(value, memoryview):
        try:
            s = bytes(value).decode('utf-8')
        except Exception:
            return False
    elif isinstance(value, bytes):
        try:
            s = value.decode('utf-8')
        except Exception:
            return False
    else:
        # str
        s = str(value)
    return s.startswith("$2a$") or s.startswith("$2b$") or s.startswith("$2y$")

def check_password(plain_password: str, hashed_password) -> bool:
    """Vérifie mot de passe en gérant types retournés par MySQL."""
    if hashed_password is None:
        return False
    if isinstance(hashed_password, memoryview):
        hashed = bytes(hashed_password)
    elif isinstance(hashed_password, str):
        hashed = hashed_password.encode('utf-8')
    else:
        hashed = hashed_password  # bytes
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed)
    except (ValueError, TypeError):
        return False

# -----------------------------
# Initialisation
# -----------------------------
creer_base_et_table()

# -----------------------------
# Ajouter utilisateur (inscription)
# -----------------------------
def ajouter_utilisateur(nom, email, mdp, role='user'):
    conn = connexion_mysql()
    if conn:
        cursor = conn.cursor()
        try:
            # hash avant insertion — stocké en BLOB (bytes)
            hashed = hash_password(mdp)
            cursor.execute(
                "INSERT INTO utilisateurs (nom,email,mot_de_passe,role) VALUES (%s,%s,%s,%s)",
                (nom, email, hashed, role)
            )
            conn.commit()
            messagebox.showinfo("Succès", f"Utilisateur {nom} ajouté!")
            # récupérer utilisateur (nom,email)
            cursor.execute("SELECT nom,email,role FROM utilisateurs WHERE email=%s", (email,))
            utilisateur = cursor.fetchone()
            global current_user, current_user_role
            if utilisateur:
                current_user = (utilisateur[0], utilisateur[1])
                current_user_role = utilisateur[2]
                goProfil()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erreur", "Email déjà utilisé!")
        finally:
            cursor.close()
            conn.close()

# -----------------------------
# Login (authentification) - corrigé
# -----------------------------
def login(email, mdp):
    global current_user, current_user_role  # déclaration en tête pour éviter SyntaxError

    conn = connexion_mysql()
    if not conn:
        messagebox.showerror("Erreur", "Impossible de se connecter à la base")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, email, mot_de_passe, role FROM utilisateurs WHERE email=%s", (email,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Erreur", "Email ou mot de passe incorrect")
        cursor.close()
        conn.close()
        return

    user_id, nom_db, email_db, pwd_blob, role_db = row

    # pwd_blob peut être memoryview, bytes ou str
    if isinstance(pwd_blob, memoryview):
        pwd_bytes = bytes(pwd_blob)
    else:
        pwd_bytes = pwd_blob

    # Si c'est un hash bcrypt valide :
    if is_bcrypt_hash(pwd_bytes):
        if check_password(mdp, pwd_bytes):
            current_user = (nom_db, email_db)
            current_user_role = role_db
            messagebox.showinfo("Succès", "Connexion réussie !")
            # rediriger selon role
            if role_db == 'admin':
                admin_dashboard()
            elif role_db == 'rh':
                rh_dashboard()
            else:
                user_dashboard()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect")
    else:
        # mot_de_passe non hashé (héritage) — comparer en clair puis migrer si OK
        try:
            # Convertir bytes -> str si nécessaire
            if isinstance(pwd_bytes, bytes):
                plain_stored = pwd_bytes.decode('utf-8')
            else:
                plain_stored = str(pwd_bytes)
        except Exception:
            plain_stored = None

        if plain_stored is not None and plain_stored == mdp:
            # mot de passe correct en clair — migrer vers bcrypt
            new_hash = hash_password(mdp)  # bytes
            try:
                cursor.execute("UPDATE utilisateurs SET mot_de_passe=%s WHERE id=%s", (new_hash, user_id))
                conn.commit()
                messagebox.showinfo("Info", "Mot de passe migré vers un stockage sécurisé.")
            except Exception as e:
                print("Erreur migration hash:", e)
            # connecter l'utilisateur
            current_user = (nom_db, email_db)
            current_user_role = role_db
            messagebox.showinfo("Succès", "Connexion réussie !")
            if role_db == 'admin':
                admin_dashboard()
            elif role_db == 'rh':
                rh_dashboard()
            else:
                user_dashboard()
        else:
            messagebox.showerror("Erreur", "Email ou mot de passe incorrect")

    cursor.close()
    conn.close()

# -----------------------------
# open_create_user (admin) - modifié pour hasher mdp
# -----------------------------
def open_create_user():
    # Fenêtre popup
    popup = tk.Toplevel(app)
    popup.title("Créer un utilisateur")
    popup.geometry("320x300")
    popup.config(bg=couleurFondImage)

    tk.Label(popup, text="Créer un nouvel utilisateur", font=("Arial", 12, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=10)

    tk.Label(popup, text="Nom :", bg=couleurFondImage, fg="white").pack()
    entryNom = tk.Entry(popup)
    entryNom.pack(pady=2)

    tk.Label(popup, text="Email :", bg=couleurFondImage, fg="white").pack()
    entryEmail = tk.Entry(popup)
    entryEmail.pack(pady=2)

    tk.Label(popup, text="Mot de passe :", bg=couleurFondImage, fg="white").pack()
    entryMDP = tk.Entry(popup, show="*")
    entryMDP.pack(pady=2)

    tk.Label(popup, text="Rôle :", bg=couleurFondImage, fg="white").pack(pady=2)
    var_role = tk.StringVar(popup)
    var_role.set("user")  # Par défaut
    optionRole = tk.OptionMenu(popup, var_role, "admin", "rh", "chercheur", "user")
    optionRole.pack()

    def submit_new_user():
        nom = entryNom.get().strip()
        email = entryEmail.get().strip()
        mdp = entryMDP.get().strip()
        role = var_role.get()

        if not nom or not email or not mdp:
            messagebox.showwarning("Champs vides", "Veuillez remplir tous les champs.")
            return

        try:
            # On utilise la fonction ajouter_utilisateur qui hash déjà le mot de passe
            ajouter_utilisateur(nom, email, mdp, role)
            popup.destroy()
            admin_manage_users()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erreur", "Email déjà utilisé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur MySQL: {e}")

    tk.Button(popup, text="Créer", bg="#0d47a1", fg="white",
              command=submit_new_user).pack(pady=10)

    tk.Button(popup, text="Annuler", bg="#b71c1c", fg="white",
              command=popup.destroy).pack()

# -----------------------------
# Gestion utilisateurs (admin) - je laisse tes fonctions originales
# -----------------------------
def admin_manage_users():
    """Affiche le tableau de gestion des utilisateurs (admin only)."""
    for w in mainFrame.winfo_children():
        w.destroy()

    tk.Label(mainFrame, text="Gestion des utilisateurs", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=10)

    # Frame pour la liste + actions
    frame_list = tk.Frame(mainFrame, bg=couleurFondImage)
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)

    # En-têtes
    header = tk.Frame(frame_list, bg=couleurFondImage)
    header.pack(fill="x")
    tk.Label(header, text="ID", width=5, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=0)
    tk.Label(header, text="Nom", width=20, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=1)
    tk.Label(header, text="Email", width=25, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=2)
    tk.Label(header, text="Rôle", width=12, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=3)
    tk.Label(header, text="Actions", width=20, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=4)

    # Canvas + scrollbar pour la liste si beaucoup d'utilisateurs
    canvas = tk.Canvas(frame_list, bg=couleurFondImage, highlightthickness=0)
    vsb = tk.Scrollbar(frame_list, orient="vertical", command=canvas.yview)
    list_frame = tk.Frame(canvas, bg=couleurFondImage)
    list_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=list_frame, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # Zone actions en bas
    actions_frame = tk.Frame(mainFrame, bg=couleurFondImage)
    actions_frame.pack(fill="x", pady=6)
    tk.Button(actions_frame, text="Rafraîchir", bg="#0d47a1", fg="white", command=lambda: refresh_user_list(list_frame)).pack(side="left", padx=5)
    tk.Button(actions_frame, text="Créer utilisateur", bg="#0d47a1", fg="white", command=open_create_user).pack(side="left", padx=5)
    tk.Button(actions_frame, text="Retour", bg="#555", fg="white", command=admin_dashboard).pack(side="right", padx=5)

    # Remplir la liste
    refresh_user_list(list_frame)

def refresh_user_list(container):
    """Rafraîchit la liste des utilisateurs dans le container fourni."""
    # Effacer l'ancien contenu
    for widget in container.winfo_children():
        widget.destroy()

    conn = connexion_mysql()
    if not conn:
        tk.Label(container, text="Erreur de connexion à la base", bg=couleurFondImage, fg="white").pack()
        return

    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, email, IFNULL(role,'user') FROM utilisateurs ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        tk.Label(container, text="Aucun utilisateur trouvé", bg=couleurFondImage, fg="white").pack()
        return

    # Afficher chaque utilisateur
    for i, (uid, nom, email, role) in enumerate(rows):
        row_frame = tk.Frame(container, bg=couleurFondImage)
        row_frame.pack(fill="x", pady=2)

        tk.Label(row_frame, text=str(uid), width=5, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=0)
        tk.Label(row_frame, text=nom, width=20, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=1)
        tk.Label(row_frame, text=email, width=25, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=2)
        tk.Label(row_frame, text=role, width=12, bg=couleurFondImage, fg="white", anchor="w").grid(row=0, column=3)

        # Actions : supprimer, changer rôle, reset mdp
        btn_delete = tk.Button(row_frame, text="Supprimer", bg="#b71c1c", fg="white",
                               command=lambda uid=uid, email=email: confirm_delete_user(uid, email))
        btn_delete.grid(row=0, column=4, padx=2)

        btn_role = tk.Button(row_frame, text="Changer rôle", bg="#f57c00", fg="white",
                             command=lambda uid=uid: open_change_role(uid))
        btn_role.grid(row=0, column=5, padx=2)

        btn_reset = tk.Button(row_frame, text="Reset MDP", bg="#00695c", fg="white",
                              command=lambda uid=uid: confirm_reset_password(uid))
        btn_reset.grid(row=0, column=6, padx=2)

def confirm_delete_user(user_id, email):
    """Confirme et supprime l'utilisateur (ne pas permettre à admin de se supprimer lui-même)."""
    # Empêcher suppression de l'admin connecté (si tu veux)
    if current_user and current_user[1] == email:
        messagebox.showwarning("Action interdite", "Vous ne pouvez pas supprimer votre propre compte.")
        return

    if messagebox.askyesno("Confirmer", f"Supprimer l'utilisateur {email} ?"):
        delete_user(user_id)
        admin_manage_users()  # refresh

def delete_user(user_id):
    conn = connexion_mysql()
    if not conn:
        messagebox.showerror("Erreur", "Connexion DB échouée")
        return
    cursor = conn.cursor()
    cursor.execute("DELETE FROM utilisateurs WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Suppression", "Utilisateur supprimé avec succès")

def open_change_role(user_id):
    """Ouvre un mini-dialogue pour changer le rôle."""
    popup = tk.Toplevel(app)
    popup.title("Changer rôle")
    popup.geometry("300x140")
    popup.config(bg=couleurFondImage)

    tk.Label(popup, text="Choisir un rôle :", bg=couleurFondImage, fg="white").pack(pady=8)
    var_role = tk.StringVar(popup)
    var_role.set("user")  # valeur par défaut
    option = tk.OptionMenu(popup, var_role, "admin", "rh", "chercheur", "user")
    option.config(width=20)
    option.pack(pady=5)

    def apply_role():
        change_role(user_id, var_role.get())
        popup.destroy()
        admin_manage_users()

    tk.Button(popup, text="Valider", bg="#0d47a1", fg="white", command=apply_role).pack(pady=8)

def change_role(user_id, new_role):
    conn = connexion_mysql()
    if not conn:
        messagebox.showerror("Erreur", "Connexion DB échouée")
        return
    cursor = conn.cursor()
    cursor.execute("UPDATE utilisateurs SET role=%s WHERE id=%s", (new_role, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    messagebox.showinfo("Rôle changé", "Le rôle a été mis à jour")

def confirm_reset_password(user_id):
    if messagebox.askyesno("Reset mot de passe", "Générer un mot de passe temporaire et l'appliquer ?"):
        # génère un mot de passe simple (tu peux améliorer)
        temp = "Temp1234"
        reset_password(user_id, temp)
        messagebox.showinfo("Mot de passe réinitialisé", f"Mot de passe temporaire : {temp}")

def reset_password(user_id, new_password):
    # Hasher avant d'enregistrer
    try:
        hashed = hash_password(new_password)  # bytes
    except Exception:
        hashed = new_password.encode('utf-8') if isinstance(new_password, str) else new_password

    conn = connexion_mysql()
    if not conn:
        messagebox.showerror("Erreur", "Connexion DB échouée")
        return
    cursor = conn.cursor()
    cursor.execute("UPDATE utilisateurs SET mot_de_passe=%s WHERE id=%s", (hashed, user_id))
    conn.commit()
    cursor.close()
    conn.close()

# -----------------------------
# Dashboards
# -----------------------------
def admin_dashboard():
    for w in mainFrame.winfo_children():
        w.destroy()
    tk.Button(navLateral,
        text="gestion",
        font=("Arial", 13, "bold"),
        bg="gray30",
        fg=couleur["white"],
        activebackground="#333333",
        bd=0,
        command=admin_dashboard).place(x=25, y=280)

    tk.Label(mainFrame, text="Tableau de bord Admin", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=20)
    # boutons admin utiles
    tk.Button(mainFrame, text="Gérer utilisateurs", command=admin_manage_users).pack(pady=5)
    tk.Button(mainFrame, text="Déconnexion", command=logout).pack(pady=10)

def rh_dashboard():
    for w in mainFrame.winfo_children():
        w.destroy()
        tk.Button(navLateral,
        text="votre espace",
        font=("Arial", 13, "bold"),
        bg="gray30",
        fg=couleur["white"],
        activebackground="#333333",
        bd=0,
        command=rh_dashboard).place(x=25, y=280)
    
    tk.Label(mainFrame, text="Espace RH", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=20)
    tk.Button(mainFrame, text="ajouter un offre", command=open_add_offre_window).pack(pady=5)
    tk.Button(mainFrame, text="Déconnexion", command=logout).pack(pady=10)

def user_dashboard():
    for w in mainFrame.winfo_children():
        w.destroy()
        tk.Button(navLateral,
        text="votre espace",
        font=("Arial", 13, "bold"),
        bg="gray30",
        fg=couleur["white"],
        activebackground="#333333",
        bd=0,
        command=user_dashboard).place(x=25, y=280)
    tk.Label(mainFrame, text="Espace Chercheur", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=20)
    tk.Button(mainFrame, text="Déconnexion", command=logout).pack(pady=10)

def logout():
    global current_user, current_user_role
    current_user = None
    current_user_role = None
    messagebox.showinfo("Déconnexion", "Vous avez été déconnecté.")
    update_navbar()  # met à jour le menu
    showAccueil()    # retourne à la page d'accueil


def update_navbar():
    # Efface tous les widgets du menu
    for widget in navLateral.winfo_children():
        widget.destroy()

    # En-tête du menu
    tk.Label(
        navLateral,
        text="MENU",
        font=("Arial", 15, "bold"),
        bg="#0d47a1",
        fg="white",
        width=300,
        height=2
    ).place(x=0, y=0)

    # Boutons du menu principal
    y = 80
    menu_items = [
        ("Accueil", goAccueil),
        ("Profil", goProfil),
        ("Offres d'emploi", goOffres),
        ("Paramètres", goParametres),
        ("Contact", goContact)
    ]

    for text, cmd in menu_items:
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

    # Si un utilisateur est connecté → afficher le bouton Déconnexion
    if current_user:
        tk.Button(
            navLateral,
            text="Déconnexion",
            font=("Arial", 13, "bold"),
            bg="#d32f2f",
            fg="white",
            activebackground="#b71c1c",
            bd=0,
            command=logout
        ).place(x=25, y=y + 20)


# -----------------------------
# Forms : Login / Inscription / Accueil
# -----------------------------
def showLogin():
    for widget in mainFrame.winfo_children():
        widget.destroy()

    tk.Label(mainFrame, text="Connexion", font=("Arial", 16, "bold"),
             bg=couleurFondImage, fg="white").pack(pady=20)

    tk.Label(mainFrame, text="Email :", bg=couleurFondImage, fg="white").pack()
    entryEmail = tk.Entry(mainFrame)
    entryEmail.pack()

    tk.Label(mainFrame, text="Mot de passe :", bg=couleurFondImage, fg="white").pack()
    entryMDP = tk.Entry(mainFrame, show="*")
    entryMDP.pack()

    tk.Button(mainFrame, text="Se connecter", bg="#0d47a1", fg="white",
              command=lambda: login(entryEmail.get(), entryMDP.get())
    ).pack(pady=10)

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

    """ tk.Label(mainFrame, text="votre role :", bg=couleurFondImage, fg="white").pack()
    entryrole = tk.Entry(mainFrame)
    entryrole.pack()"""

    tk.Button(mainFrame, text="S'inscrire", bg="#0d47a1", fg="white",
              command=lambda: ajouter_utilisateur(entryNom.get(), entryEmail.get(), entryMDP.get())).pack(pady=10)

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
        text="Se connecter",
        font=("Arial", 11, "underline"),
        bg=couleurFondImage,
        fg="white",
        cursor="hand2"
    )
    lienLogin.place(relx=0.5, rely=0.65, anchor="center")
    lienLogin.bind("<Button-1>", lambda e: showLogin())

    # Lien "S'inscrire"
    lienInscription = tk.Label(
        mainFrame,
        text="S'inscrire",
        font=("Arial", 11, "underline"),
        bg=couleurFondImage,
        fg="white",
        cursor="hand2"
    )
    lienInscription.place(relx=0.5, rely=0.70, anchor="center")
    lienInscription.bind("<Button-1>", lambda e: showInscription())

#---------------------rh-----------------

def open_add_offre_window():
    # Crée une nouvelle fenêtre (popup)
    add_window = Toplevel()
    add_window.title("Ajouter une offre")
    add_window.geometry("400x500")
    
    Label(add_window, text="Titre :", font=("Arial", 12)).pack(pady=5)
    titre_entry = Entry(add_window, width=40)
    titre_entry.pack(pady=5)

    Label(add_window, text="Description :", font=("Arial", 12)).pack(pady=5)
    description_text = Text(add_window, width=40, height=5)
    description_text.pack(pady=5)

    Label(add_window, text="Lieu :", font=("Arial", 12)).pack(pady=5)
    lieu_entry = Entry(add_window, width=40)
    lieu_entry.pack(pady=5)

    Label(add_window, text="Salaire :", font=("Arial", 12)).pack(pady=5)
    salaire_entry = Entry(add_window, width=40)
    salaire_entry.pack(pady=5)

    Label(add_window, text="Type (CDI, Stage, ...):", font=("Arial", 12)).pack(pady=5)
    type_entry = Entry(add_window, width=40)
    type_entry.pack(pady=5)

    def save_offre():
        titre = titre_entry.get().strip()
        description = description_text.get("1.0", "end-1c").strip()
        lieu = lieu_entry.get().strip()
        salaire = salaire_entry.get().strip()
        type_offre = type_entry.get().strip()

        if not titre or not description or not lieu or not type_offre:
            messagebox.showwarning("Champs manquants", "Merci de remplir tous les champs.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin_py",
                password="admin",
                database="projet"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO offres (titre, description, lieu, salaire, type)
                VALUES (%s, %s, %s, %s, %s)
            """, (titre, description, lieu, salaire, type_offre))
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Offre ajoutée avec succès ✅")
            add_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout de l'offre : {err}")

    Button(add_window, text="Enregistrer l'offre", command=save_offre, bg="#4CAF50", fg="white").pack(pady=15)

# -----------------------------
# Contact and navigation
# -----------------------------
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

# -----------------------------
# Navbar lateral and menu
# -----------------------------
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
        tk.Button(mainFrame, text="Se connecter", bg="#0d47a1", fg="white",
                  command=showLogin).pack(pady=10)

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
        if navIcon:
            navbarBtn.config(image=navIcon)
        btnEtat = False
    else:
        for x in range(-300, 1, 10):
            navLateral.place(x=x, y=0)
            app.update()
        navLateral.place(x=0, y=0)
        topFrame.tkraise()
        if closeIcon:
            navbarBtn.config(image=closeIcon)
        btnEtat = True

navbarBtn.config(command=toggleMenu)



# === PAGE PAR DÉFAUT ===
showAccueil()

# === BOUCLE PRINCIPALE ===
app.mainloop()
