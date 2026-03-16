import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import csv
import base_donnees
from logique import arbitrer_candidature
import sys

# --- GESTION DES REPERTOIRES POUR LA COMPILATION ---
def resource_path(relative_path):
    """ Obtenir le chemin absolu du fichier, adapté à la compilation PyInstaller """
    try:
        # Chemin temporaire pour les exécutables PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Chemin normal pour le développement
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# --- CONFIGURATION THEME PROFESSIONNEL (Nuances de Gris) ---
ctk.set_appearance_mode("Light")
# On utilise des couleurs sobres
CouleurPrincipale = "#2C3E50" # Gris foncé bleuté institutionnel
CouleurSecondaire = "#ECF0F1" # Gris très clair pour les fonds
CouleurAccent = "#7F8C8D" # Gris moyen
TexteCouleur = "#333333"

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cour Suprême - Portail Sécurisé")
        self.geometry("1100x700")
        self.minsize(950, 650)
        self.configure(fg_color=CouleurSecondaire)
        
        self.campagne_actuelle = None

        # Conteneur principal qui va héberger les différentes vues
        self.conteneur = ctk.CTkFrame(self, fg_color="transparent")
        self.conteneur.pack(fill="both", expand=True)

        # Initialisation des Vues
        self.vue_connexion = VueConnexion(self.conteneur, self)
        self.vue_session = VueConfigurationSession(self.conteneur, self)
        self.vue_principale = None # Sera initialisée après connexion

        # Afficher la connexion au démarrage
        self.afficher_vue(self.vue_connexion)

    def afficher_vue(self, vue):
        # Cacher toutes les vues
        for v in self.conteneur.winfo_children():
            v.pack_forget()
        # Afficher la vue demandée
        vue.pack(fill="both", expand=True)

    def lancer_session_principale(self):
        # Une fois la campagne définie, on lance le main dashboard
        self.campagne_actuelle = base_donnees.recuperer_campagne_active()
        if not self.vue_principale:
            self.vue_principale = VuePrincipale(self.conteneur, self)
        self.afficher_vue(self.vue_principale)


class VueConnexion(ctk.CTkFrame):
    def __init__(self, master, controlleur):
        super().__init__(master, fg_color="transparent")
        self.controlleur = controlleur

        # Centrage du contenu
        cadre_central = ctk.CTkFrame(self, width=400, height=450, fg_color="white", corner_radius=15, border_width=1, border_color="gray80")
        cadre_central.place(relx=0.5, rely=0.5, anchor="center")
        cadre_central.pack_propagate(False)

        # Logo
        try:
            image_path = resource_path("assets/OIP.webp")
            image_logo = ctk.CTkImage(light_image=Image.open(image_path), dark_image=Image.open(image_path), size=(100, 100))
            lbl_logo = ctk.CTkLabel(cadre_central, image=image_logo, text="")
            lbl_logo.pack(pady=(30, 10))
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            pass

        ctk.CTkLabel(cadre_central, text="PORTAIL ADMINISTRATION", font=ctk.CTkFont(family="Arial", size=20, weight="bold"), text_color=CouleurPrincipale).pack(pady=(0, 20))

        self.entree_util = ctk.CTkEntry(cadre_central, placeholder_text="👤 Nom d'utilisateur", height=45, corner_radius=8, font=ctk.CTkFont(size=14))
        self.entree_util.pack(fill="x", padx=40, pady=10)

        self.entree_mdp = ctk.CTkEntry(cadre_central, placeholder_text="🔒 Mot de passe", show="*", height=45, corner_radius=8, font=ctk.CTkFont(size=14))
        self.entree_mdp.pack(fill="x", padx=40, pady=10)

        btn_connexion = ctk.CTkButton(cadre_central, text="CONNEXION", command=self.verifier_connexion, height=50, corner_radius=8, fg_color=CouleurPrincipale, hover_color="#1A252F", font=ctk.CTkFont(weight="bold", size=14))
        btn_connexion.pack(fill="x", padx=40, pady=(30, 20))

    def verifier_connexion(self):
        util = self.entree_util.get().strip()
        mdp = self.entree_mdp.get().strip()

        if base_donnees.verifier_login(util, mdp):
            # Succès -> Passer au choix de session
            self.controlleur.afficher_vue(self.controlleur.vue_session)
            self.controlleur.vue_session.rafraichir_statut()
        else:
            messagebox.showerror("Accès Refusé", "Identifiants incorrects.")


class VueConfigurationSession(ctk.CTkFrame):
    def __init__(self, master, controlleur):
        super().__init__(master, fg_color="transparent")
        self.controlleur = controlleur
        self.nouveau_fichier = None

        cadre = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1, border_color="gray80")
        cadre.place(relx=0.5, rely=0.5, anchor="center")
        cadre.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(cadre, text="DÉMARRAGE DE L'ÉLECTION", font=ctk.CTkFont(size=22, weight="bold"), text_color=CouleurPrincipale).grid(row=0, column=0, columnspan=2, pady=(30, 20))

        # --- Partie Gauche: Continuer Session Active ---
        cadre_existant = ctk.CTkFrame(cadre, fg_color="gray95", corner_radius=10)
        cadre_existant.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(cadre_existant, text="Session en cours", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20,10))
        self.lbl_session = ctk.CTkLabel(cadre_existant, text="Recherche...", text_color="dim gray")
        self.lbl_session.pack(pady=10)
        
        self.btn_continuer = ctk.CTkButton(cadre_existant, text="Continuer cette Campagne", command=self.continuer_session, fg_color=CouleurAccent, hover_color="dim gray")
        self.btn_continuer.pack(pady=20, padx=20)

        # --- Partie Droite: Nouvelle Session ---
        cadre_nouveau = ctk.CTkFrame(cadre, fg_color="gray95", corner_radius=10)
        cadre_nouveau.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(cadre_nouveau, text="Nouvelle Élection", font=ctk.CTkFont(weight="bold", size=16)).pack(pady=(20,10))
        
        self.entree_nom = ctk.CTkEntry(cadre_nouveau, placeholder_text="Ex: Présidentielle 2029")
        self.entree_nom.pack(fill="x", padx=30, pady=10)

        self.btn_charger = ctk.CTkButton(cadre_nouveau, text="📁 Base Électorale", command=self.choisir_fichier, fg_color="gray60", text_color="white")
        self.btn_charger.pack(pady=10)
        
        self.lbl_fichier = ctk.CTkLabel(cadre_nouveau, text="Aucun fichier", font=ctk.CTkFont(size=11))
        self.lbl_fichier.pack()

        btn_creer = ctk.CTkButton(cadre_nouveau, text="Créer et Démarrer", command=self.creer_nouvelle_session, fg_color=CouleurPrincipale)
        btn_creer.pack(pady=(20, 20), padx=20)

    def rafraichir_statut(self):
        campagne = base_donnees.recuperer_campagne_active()
        if campagne:
            self.lbl_session.configure(text=f"Campagne active : {campagne['nom']}\nBase: {os.path.basename(campagne['chemin'])}")
            self.btn_continuer.configure(state="normal")
        else:
            self.lbl_session.configure(text="Aucune campagne active.")
            self.btn_continuer.configure(state="disabled")

    def choisir_fichier(self):
        ch = filedialog.askopenfilename(title="Fichier Électoral National", filetypes=[("Excel", "*.xlsx")])
        if ch:
            self.nouveau_fichier = ch
            self.lbl_fichier.configure(text=os.path.basename(ch))

    def continuer_session(self):
        self.controlleur.lancer_session_principale()

    def creer_nouvelle_session(self):
        nom = self.entree_nom.get().strip()
        if not nom:
            messagebox.showwarning("Incomplet", "Veuillez donner un nom à cette élection.")
            return
        if not self.nouveau_fichier:
            messagebox.showwarning("Incomplet", "Une base électorale de référence est requise.")
            return
            
        base_donnees.creer_campagne(nom, self.nouveau_fichier)
        
        # On passe au main dashboard
        self.controlleur.lancer_session_principale()


class VuePrincipale(ctk.CTkFrame):
    def __init__(self, master, controlleur):
        super().__init__(master, fg_color="transparent")
        self.controlleur = controlleur
        self.campagne = self.controlleur.campagne_actuelle
        
        # Header Pro
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="white", border_width=1, border_color="gray85")
        self.header_frame.pack(fill="x", side="top")
        
        # Logo + Titre (Plus professionnel)
        cadre_top_gauche = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        cadre_top_gauche.pack(side="left", padx=20, pady=10)
        
        try:
            image_path = resource_path("assets/OIP.webp")
            img = ctk.CTkImage(light_image=Image.open(image_path), size=(40, 40))
            ctk.CTkLabel(cadre_top_gauche, image=img, text="").pack(side="left", padx=(0,15))
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            pass

        ctk.CTkLabel(cadre_top_gauche, text="COUR SUPRÊME", font=ctk.CTkFont(family="Arial Black", size=20, weight="bold"), text_color=CouleurPrincipale).pack(anchor="w")
        ctk.CTkLabel(cadre_top_gauche, text=f"Session: {self.campagne['nom']}", font=ctk.CTkFont(size=12)).pack(anchor="w")

        # Bouton Déconnexion
        ctk.CTkButton(self.header_frame, text="🔒 Déconnexion", width=100, command=self.deconnexion, fg_color="transparent", text_color="gray50", hover_color="gray90").pack(side="right", padx=20)

        # Les Onglets
        self.onglets = ctk.CTkTabview(self, corner_radius=10, fg_color="white", border_width=1, border_color="gray85")
        self.onglets.pack(fill="both", expand=True, padx=20, pady=20)

        self.onglets.add("STATISTIQUES")
        self.onglets.add("DÉPÔT CANDIDATURE")

        # Init Vues Internes
        self.vue_tableau = VueTableauInterne(self.onglets.tab("STATISTIQUES"), self.campagne['id'])
        self.vue_tableau.pack(fill="both", expand=True)

        self.vue_formulaire = VueFormulaireInterne(self.onglets.tab("DÉPÔT CANDIDATURE"), self)
        self.vue_formulaire.pack(fill="both", expand=True)

        self.onglets.configure(command=self.on_tab_change)

    def on_tab_change(self):
        if self.onglets.get() == "STATISTIQUES":
            self.vue_tableau.rafraichir()

    def deconnexion(self):
        self.controlleur.campagne_actuelle = None
        self.controlleur.afficher_vue(self.controlleur.vue_connexion)


class VueTableauInterne(ctk.CTkFrame):
    def __init__(self, master, id_campagne):
        super().__init__(master, fg_color="transparent")
        self.id_campagne = id_campagne
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- Barre supérieure : Statistiques + Recherche + Export (Sur une seule ligne) ---
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=40)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.lbl_stats = ctk.CTkLabel(top_bar, text="DOSSIERS: 0 | VALIDÉS: 0 | REJETÉS: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color=CouleurPrincipale)
        self.lbl_stats.pack(side="left", padx=(0, 20))
        
        self.entree_recherche = ctk.CTkEntry(top_bar, placeholder_text="🔍 Rechercher (Nom, NIN)...", width=250, height=30)
        self.entree_recherche.pack(side="left", padx=10)
        self.entree_recherche.bind("<KeyRelease>", self.rafraichir)

        self.btn_export = ctk.CTkButton(top_bar, text="📥 Exporter (CSV)", width=120, height=30, command=self.exporter_donnees, fg_color=CouleurPrincipale)
        self.btn_export.pack(side="right")

        # --- Liste DataGrid (Prend 90% de l'espace) ---
        self.liste = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=0, border_width=1, border_color="gray85")
        self.liste.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # En-tête Tableau
        header = ctk.CTkFrame(self.liste, fg_color="gray95", corner_radius=0)
        header.pack(fill="x")
        header.grid_columnconfigure((0, 1, 2, 3), weight=1)
        header.grid_columnconfigure(4, weight=2)
        
        cols = ["NIN", "IDENTITÉ", "NAISSANCE", "DÉCISION", "OBSERVATIONS"]
        for i, c in enumerate(cols):
            ctk.CTkLabel(header, text=c, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray30").grid(row=0, column=i, sticky="w", padx=10, pady=5)

        self.conteneur = ctk.CTkFrame(self.liste, fg_color="transparent")
        self.conteneur.pack(fill="both", expand=True)

        self.rafraichir()

    def rafraichir(self, event=None):
        stats = base_donnees.recuperer_statistiques(self.id_campagne)
        self.lbl_stats.configure(text=f"DOSSIERS : {stats['total']}   |   VALIDÉS : {stats['acceptees']}   |   REJETÉS : {stats['rejetees']}")
        
        for w in self.conteneur.winfo_children():
            w.destroy()

        terme_recherche = self.entree_recherche.get().lower()

        candidats = base_donnees.recuperer_tous_les_candidats(self.id_campagne)
        
        for idx, c in enumerate(candidats):
            identite = f"{c['nom'].upper()} {c['prenom']}"
            
            # Filtre de recherche
            if terme_recherche and (terme_recherche not in identite.lower() and terme_recherche not in c['nin']):
                continue

            bg = "white" if idx % 2 == 0 else "gray98"
            ligne = ctk.CTkFrame(self.conteneur, fg_color=bg, corner_radius=0)
            ligne.pack(fill="x")
            ligne.grid_columnconfigure((0, 1, 2, 3), weight=1)
            ligne.grid_columnconfigure(4, weight=2)
            
            ctk.CTkLabel(ligne, text=c['nin'], text_color="gray40").grid(row=0, column=0, sticky="w", padx=10, pady=8)
            ctk.CTkLabel(ligne, text=f"{c['nom'].upper()} {c['prenom']}").grid(row=0, column=1, sticky="w", padx=10)
            ctk.CTkLabel(ligne, text=c['date_naissance']).grid(row=0, column=2, sticky="w", padx=10)
            ctk.CTkLabel(ligne, text=c['statut'], text_color=CouleurPrincipale if c['statut']=="Acceptée" else "dim gray", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, sticky="w", padx=10)
            ctk.CTkLabel(ligne, text=(c['motif_rejet'] or "Dossier Conforme"), wraplength=250, justify="left", text_color="gray50").grid(row=0, column=4, sticky="w", padx=10)

    def exporter_donnees(self):
        candidats = base_donnees.recuperer_tous_les_candidats(self.id_campagne)
        if not candidats:
            messagebox.showinfo("Export", "Aucune donnée à exporter.")
            return

        chemin = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Fichiers CSV", "*.csv")], title="Générer Rapport")
        if not chemin:
            return

        try:
            with open(chemin, mode='w', newline='', encoding='utf-8-sig') as fichier:
                writer = csv.writer(fichier, delimiter=';')
                writer.writerow(["NIN", "Prénom", "Nom", "Date de Naissance", "Lieu de Naissance", "Nationalité", "Statut", "Motif"])
                for c in candidats:
                    writer.writerow([c['nin'], c['prenom'], c['nom'], c['date_naissance'], c['lieu_naissance'], c['nationalite'], c['statut'], c['motif_rejet'] or "Dossier Conforme"])
            messagebox.showinfo("Succès", f"Les données ont été exportées avec succès dans :\n{chemin}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {e}")


class VueFormulaireInterne(ctk.CTkFrame):
    def __init__(self, master, vue_principale):
        super().__init__(master, fg_color="transparent")
        self.vue_principale = vue_principale
        self.chemin_parrainage = None
        
        self.grid_columnconfigure((0, 1), weight=1)
        
        # Style formulaire pro
        style = {"height": 40, "corner_radius": 0, "border_width": 1, "border_color": "gray80", "fg_color": "gray98"}
        
        ctk.CTkLabel(self, text="SAISIE DES INFORMATIONS", font=ctk.CTkFont(weight="bold", size=14), text_color="gray40").grid(row=0, column=0, columnspan=2, pady=20, sticky="w", padx=40)

        self.prenom = ctk.CTkEntry(self, placeholder_text="Prénom(s)", **style)
        self.prenom.grid(row=1, column=0, padx=40, pady=10, sticky="ew")
        
        self.nom = ctk.CTkEntry(self, placeholder_text="Nom Patronymique", **style)
        self.nom.grid(row=1, column=1, padx=40, pady=10, sticky="ew")

        self.naissance = ctk.CTkEntry(self, placeholder_text="Date de Naissance (JJ/MM/AAAA)", **style)
        self.naissance.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        self.lieu = ctk.CTkEntry(self, placeholder_text="Lieu de Naissance", **style)
        self.lieu.grid(row=2, column=1, padx=40, pady=10, sticky="ew")

        self.nationalite = ctk.CTkEntry(self, **style)
        self.nationalite.insert(0, "Sénégalaise")
        self.nationalite.configure(state="readonly")
        self.nationalite.grid(row=3, column=0, padx=40, pady=10, sticky="ew")

        self.nin = ctk.CTkEntry(self, placeholder_text="NIN (13 chiffres)", **style)
        self.nin.grid(row=3, column=1, padx=40, pady=10, sticky="ew")

        # Fichier Parrainages Uniquement (Électoral est géré par la session)
        cadre_file = ctk.CTkFrame(self, fg_color="transparent")
        cadre_file.grid(row=4, column=0, columnspan=2, pady=20, padx=40, sticky="w")
        
        ctk.CTkButton(cadre_file, text="Parcourir...", command=self.choisir, fg_color="white", text_color=CouleurPrincipale, border_width=1, border_color="gray70", hover_color="gray95", corner_radius=0).pack(side="left")
        self.lbl_p = ctk.CTkLabel(cadre_file, text="Aucun fichier de parrainage Excel (.xlsx) sélectionné", text_color="dim gray")
        self.lbl_p.pack(side="left", padx=15)

        # Validation
        ctk.CTkButton(self, text="ENREGISTRER LA CANDIDATURE", command=self.valider, height=50, corner_radius=0, fg_color=CouleurPrincipale, text_color="white").grid(row=5, column=0, columnspan=2, pady=40, padx=40, sticky="ew")

    def choisir(self):
        ch = filedialog.askopenfilename(title="Parrainages du Candidat", filetypes=[("Excel", "*.xlsx")])
        if ch:
            self.chemin_parrainage = ch
            self.lbl_p.configure(text=os.path.basename(ch))

    def vider(self):
        for e in [self.prenom, self.nom, self.naissance, self.lieu, self.nin]:
            e.delete(0, 'end')
        self.chemin_parrainage = None
        self.lbl_p.configure(text="Aucun fichier de parrainage Excel (.xlsx) sélectionné")

    def valider(self):
        data = {
            'prenom': self.prenom.get().strip(),
            'nom': self.nom.get().strip(),
            'date_naissance': self.naissance.get().strip(),
            'lieu_naissance': self.lieu.get().strip(),
            'nationalite': self.nationalite.get().strip(),
            'nin': self.nin.get().strip()
        }

        if not all(data.values()) or not self.chemin_parrainage:
            messagebox.showwarning("Incomplet", "Veuillez remplir tout le formulaire et fournir le fichier de parrainage.")
            return

        campagne = self.vue_principale.campagne
        # L'arbitrage utilise le fichier electoral de la session
        accepte, motif, parrainages_valides = arbitrer_candidature(data, self.chemin_parrainage, campagne['chemin'], campagne['id'])
        
        statut = "Acceptée" if accepte else "Rejetée"

        succes, msg = base_donnees.enregistrer_candidat(
            data['prenom'], data['nom'], data['date_naissance'], data['lieu_naissance'],
            data['nationalite'], data['nin'], statut, motif, campagne_id=campagne['id'], parrainages=parrainages_valides
        )

        if succes:
            titre = "Dossier Validé" if accepte else "Dossier Rejeté"
            messagebox.showinfo(titre, f"Décision d'arbitrage rendue : {statut.upper()}\n\n{motif if not accepte else 'Conforme aux normes édictées par la Cour.'}")
            self.vider()
            self.vue_principale.onglets.set("STATISTIQUES")
            self.vue_principale.vue_tableau.rafraichir()
        else:
            messagebox.showerror("Erreur Base de Données", msg)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
