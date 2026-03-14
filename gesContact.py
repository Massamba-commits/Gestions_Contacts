import sqlite3
from tkinter import Listbox, END, SINGLE
from tkinter import messagebox
import customtkinter as ctk
import os
import sys

# ══════════════════════════════════════════════════════════════════════
#  CHEMIN DYNAMIQUE — ✅ CORRIGÉ
# ══════════════════════════════════════════════════════════════════════
if getattr(sys, 'frozen', False):
    # Dans le .exe installé → stocke dans AppData (toujours accessible)
    dossier = os.path.join(os.environ['APPDATA'], 'GestionContacts')
    os.makedirs(dossier, exist_ok=True)  # crée le dossier automatiquement
else:
    # En développement normal
    dossier = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(dossier, "contacts.db")

# ══════════════════════════════════════════════════════════════════════
#  COULEURS
# ══════════════════════════════════════════════════════════════════════
BG        = "#0A3C55"
CARD      = "#022C41"
ACCENT    = "#4f8ef7"
ACCENT2   = "#CF340D"
ACCENT3   = "#300ABA"
TEXT      = "#ffffff"
SUBTEXT   = "#7b7f9e"
GREEN     = "#06da0d"
HIGHLIGHT = "#1a3a6a"

# ══════════════════════════════════════════════════════════════════════
#  THÈME
# ══════════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ══════════════════════════════════════════════════════════════════════
#  BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════════════
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Prenom TEXT NOT NULL,
    Nom TEXT NOT NULL,
    Telephone TEXT NOT NULL,
    Email TEXT)''')
conn.commit()
conn.close()

# ══════════════════════════════════════════════════════════════════════
#  FONCTIONS
# ══════════════════════════════════════════════════════════════════════

def ajoutercontact():
    prenom    = val_prenom.get().strip()
    nom       = val_nom.get().strip()
    telephone = val_telephone.get().strip()
    email     = val_Email.get().strip()

    if not (prenom and nom and telephone):
        messagebox.showwarning("Attention", "Tous les champs obligatoires")
        return
    if not telephone.isdigit():
        messagebox.showinfo("Erreur", "Seulement des chiffres autorisés"); return
    elif len(telephone) != 9:
        messagebox.showinfo("Incorrect", "Numéro invalide — 9 chiffres requis"); return
    elif not prenom.isalpha() or not nom.isalpha():
        messagebox.showinfo("Erreur", "Seulement des lettres pour prénom/nom"); return

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE Telephone=(?)', [telephone])
    if cursor.fetchone():
        messagebox.showinfo("Erreur", "Ce numéro existe déjà")
        conn.close(); return

    cursor.execute(
        'INSERT INTO contacts(Prenom,Nom,Telephone,Email) VALUES (?,?,?,?)',
        (prenom, nom, telephone, email))
    conn.commit()
    conn.close()
    for e in [val_prenom, val_nom, val_telephone, val_Email]:
        e.delete(0, END)
    afficherContact()
    messagebox.showinfo("Succès", "Contact ajouté avec succès")


def afficherContact():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Prenom,Nom,Telephone,Email FROM contacts")
    rows = cursor.fetchall()
    conn.close()
    listeContact.delete(0, END)
    for contact in rows:
        email_str = f" | ✉ {contact[3]}" if contact[3] else ""
        listeContact.insert(END, f"{contact[0]} : {contact[1]} : {contact[2]}{email_str}")
    counter_label.configure(text=f"{len(rows)} contact(s)")


def supprimerContact():
    selection = listeContact.curselection()
    if not selection:
        messagebox.showwarning("Attention", "Sélectionnez un contact"); return
    if not messagebox.askyesno("Confirmation", "Supprimer ce contact ?"):
        return
    contact = listeContact.get(selection[0])
    prenom  = contact.split(" : ")[0].strip()
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE Prenom=(?)", (prenom,))
    conn.commit()
    conn.close()
    afficherContact()


def UpdateContact():
    selection = listeContact.curselection()
    if not selection:
        messagebox.showwarning("Attention", "Sélectionnez un contact"); return

    prenom    = val_prenom.get().strip()
    nom       = val_nom.get().strip()
    telephone = val_telephone.get().strip()
    email     = val_Email.get().strip()

    if not (prenom and nom and telephone):
        messagebox.showwarning("Attention", "Remplissez les champs"); return

    contact      = listeContact.get(selection[0])
    ancienprenom = contact.split(" : ")[0].strip()

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET Prenom=?, Nom=?, Telephone=?, Email=? WHERE Prenom=?",
        (prenom, nom, telephone, email, ancienprenom))
    conn.commit()
    conn.close()
    afficherContact()
    messagebox.showinfo("Succès", "Contact mis à jour")


def charger_contact(event):
    selection = listeContact.curselection()
    if not selection:
        return
    contact = listeContact.get(selection[0])
    try:
        parties = contact.split(" : ")
        val_prenom.delete(0, END);    val_prenom.insert(0, parties[0].strip())
        val_nom.delete(0, END);       val_nom.insert(0, parties[1].strip())
        val_telephone.delete(0, END); val_telephone.insert(0, parties[2].split(" |")[0].strip())
        val_Email.delete(0, END)
        if "✉" in contact:
            val_Email.insert(0, contact.split("✉ ")[1].strip())
    except Exception:
        pass


def rechercher(event=None):
    filtre = val_search.get().strip()
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Prenom,Nom,Telephone,Email FROM contacts")
    rows = cursor.fetchall()
    conn.close()
    if filtre:
        rows = [r for r in rows if filtre.lower() in r[0].lower()
                or filtre.lower() in r[1].lower() or filtre in r[2]]
    listeContact.delete(0, END)
    for c in rows:
        email_str = f" | ✉ {c[3]}" if c[3] else ""
        listeContact.insert(END, f"{c[0]} : {c[1]} : {c[2]}{email_str}")
    counter_label.configure(text=f"{len(rows)} résultat(s)")


def fermer():
    fen.quit()
    fen.destroy()


# ══════════════════════════════════════════════════════════════════════
#  FENÊTRE
# ══════════════════════════════════════════════════════════════════════
fen = ctk.CTk()
fen.geometry("1050x900")
fen.title("application de gestion de contact téléphonique")
fen.resizable(1, 1)
fen.configure(fg_color=HIGHLIGHT)
try:
    fen.iconbitmap("25489.ico")
except Exception:
    pass

# ── En-tête ────────────────────────────────────────────────────────────
ctk.CTkLabel(fen, text=" G E S T I O N   D E S   C O N T A C T S",
             font=("Georgia", 20, "bold"), text_color=TEXT).pack(pady=16)

ctk.CTkFrame(fen, fg_color=SUBTEXT, height=1, width=600).pack(pady=(0, 14))

# ── Carte formulaire ───────────────────────────────────────────────────
form_card = ctk.CTkFrame(fen, fg_color=CARD, corner_radius=16)
form_card.pack(padx=40, pady=(0, 10), fill="x")

def champ_form(parent, icone, label, placeholder, y_offset):
    ctk.CTkLabel(parent, text=f"{icone}  {label}",
                 font=("Arial", 11, "bold"),
                 text_color=TEXT).place(x=20, y=y_offset)
    e = ctk.CTkEntry(parent,
                     placeholder_text=placeholder,
                     height=38, width=280,
                     corner_radius=10,
                     fg_color=TEXT,
                     border_color=SUBTEXT,
                     border_width=1,
                     text_color=CARD,
                     placeholder_text_color=SUBTEXT,
                     font=("Consolas", 12))
    e.place(x=200, y=y_offset)
    return e

val_prenom    = champ_form(form_card, "👤", "Prénom *",     "ex: Massamba",           20)
val_nom       = champ_form(form_card, "👤", "Nom *",        "ex: Diouf",              75)
val_telephone = champ_form(form_card, "📞", "Téléphone *",  "ex: 770971589",         130)
val_Email     = champ_form(form_card, "✉️", "Adresse mail", "ex: massamba@gmail.com", 185)

form_card.configure(height=248)

# ── Boutons ────────────────────────────────────────────────────────────
btn_frame = ctk.CTkFrame(fen, fg_color="transparent")
btn_frame.pack(padx=40, pady=8, fill="x")

ctk.CTkButton(btn_frame, width=160, text="➕  Ajouter",
              height=42, corner_radius=12,
              font=("Arial", 12, "bold"),
              fg_color=GREEN, hover_color="#04b80b",
              cursor="hand2", command=ajoutercontact).pack(side="left", padx=(0, 8))

ctk.CTkButton(btn_frame, width=160, text="🗑️  Supprimer",
              height=42, corner_radius=12,
              font=("Arial", 12, "bold"),
              fg_color=ACCENT2, hover_color="#a82a0a",
              cursor="hand2", command=supprimerContact).pack(side="left", padx=(0, 8))

ctk.CTkButton(btn_frame, width=160, text="✏️  Modifier",
              height=42, corner_radius=12,
              font=("Arial", 12, "bold"),
              fg_color=ACCENT, hover_color="#3a70d4",
              cursor="hand2", command=UpdateContact).pack(side="left")

# ── Séparateur ─────────────────────────────────────────────────────────
ctk.CTkFrame(fen, fg_color=SUBTEXT, height=1, width=600).pack(pady=(8, 10))

# ── Carte liste + recherche ────────────────────────────────────────────
list_card = ctk.CTkFrame(fen, fg_color=CARD, corner_radius=16)
list_card.pack(padx=40, pady=(0, 10), fill="both", expand=True)

list_header = ctk.CTkFrame(list_card, fg_color="transparent")
list_header.pack(fill="x", padx=16, pady=(12, 6))

ctk.CTkLabel(list_header, text="📋  Répertoire des contacts",
             font=("Georgia", 13, "bold"), text_color=ACCENT).pack(side="left")

counter_label = ctk.CTkLabel(list_header, text="0 contact(s)",
                              font=("Arial", 10), text_color=SUBTEXT)
counter_label.pack(side="right")

# Barre de recherche
search_frame = ctk.CTkFrame(list_card, fg_color=CARD, corner_radius=10, height=52)
search_frame.pack(padx=16, pady=(0, 8), fill="x")
search_frame.pack_propagate(False)

ctk.CTkLabel(search_frame, text="🔍",
             font=("Arial", 13), text_color=SUBTEXT).pack(side="left", padx=(10, 4))

val_search = ctk.CTkEntry(search_frame,
                           placeholder_text="Rechercher un contact...",
                           height=36, corner_radius=10,
                           border_width=0,
                           fg_color=CARD,
                           text_color=TEXT,
                           placeholder_text_color=SUBTEXT,
                           font=("Arial", 12))
val_search.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=8)
val_search.bind("<KeyRelease>", rechercher)
val_search.bind("<Return>", rechercher)

# Liste des contacts
listeContact = Listbox(list_card,
                       bg=CARD, fg=TEXT,
                       selectbackground=HIGHLIGHT,
                       selectforeground=TEXT,
                       font=("Consolas", 13),
                       borderwidth=0,
                       highlightthickness=0,
                       activestyle="none",
                       selectmode=SINGLE,
                       relief="flat",
                       cursor="hand2")
listeContact.pack(padx=12, pady=(2, 12), fill="both", expand=True)
listeContact.bind("<<ListboxSelect>>", charger_contact)

# ── Pied de page ───────────────────────────────────────────────────────
ctk.CTkLabel(fen, text="© 2026 Unipro — Tous droits réservés",
             font=("Times new Roman", 8, "italic"),
             fg_color=CARD, text_color=SUBTEXT).pack(pady=6)

fen.protocol("WM_DELETE_WINDOW", fermer)
afficherContact()
fen.mainloop()