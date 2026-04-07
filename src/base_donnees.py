import sqlite3
import os

NOM_BD = "cour_supreme.db"

def obtenir_connexion():
    return sqlite3.connect(NOM_BD)

def initialiser_base_de_donnees():
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    # 1. Table Administrateurs
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS administrateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT NOT NULL UNIQUE,
            mot_de_passe TEXT NOT NULL
        )
    ''')
    
    # 2. Table Campagnes (Sessions)
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS campagnes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_campagne TEXT NOT NULL,
            chemin_fichier_electoral TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Table Candidats (Mise à jour: liée à une campagne si on voulait, mais on simplifie ici)
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS candidats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            date_naissance TEXT NOT NULL,
            lieu_naissance TEXT NOT NULL,
            nationalite TEXT NOT NULL,
            nin TEXT NOT NULL UNIQUE,
            statut TEXT NOT NULL,
            motif_rejet TEXT,
            campagne_id INTEGER,
            date_soumission DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(campagne_id) REFERENCES campagnes(id)
        )
    ''')
    
    # Insérer un admin par défaut s'il n'y en a pas
    curseur.execute("SELECT COUNT(*) FROM administrateurs")
    if curseur.fetchone()[0] == 0:
        curseur.execute("INSERT INTO administrateurs (nom_utilisateur, mot_de_passe) VALUES ('admin', 'admin')")
        
    # 4. Table Parrainages Utilisés (Mise à jour pour gérer l'unicité des parrainages)
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS parrainages_utilises (
            nin TEXT PRIMARY KEY,
            candidat_id INTEGER,
            FOREIGN KEY(candidat_id) REFERENCES candidats(id)
        )
    ''')
    
    connexion.commit()
    connexion.close()

# --- Fonctions Administration ---

def verifier_login(utilisateur, mot_de_passe):
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    curseur.execute("SELECT id FROM administrateurs WHERE nom_utilisateur = ? AND mot_de_passe = ?", (utilisateur, mot_de_passe))
    resultat = curseur.fetchone()
    connexion.close()
    return resultat is not None

def creer_campagne(nom, chemin_fichier_electoral):
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    # Désactiver les autres
    curseur.execute("UPDATE campagnes SET active = 0")
    
    # Créer la nouvelle
    curseur.execute('''
        INSERT INTO campagnes (nom_campagne, chemin_fichier_electoral, active)
        VALUES (?, ?, 1)
    ''', (nom, chemin_fichier_electoral))
    
    connexion.commit()
    connexion.close()
    return True

def recuperer_campagne_active():
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    curseur.execute("SELECT id, nom_campagne, chemin_fichier_electoral FROM campagnes WHERE active = 1")
    resultat = curseur.fetchone()
    connexion.close()
    
    if resultat:
        return {"id": resultat[0], "nom": resultat[1], "chemin": resultat[2]}
    return None

# --- Fonctions Candidats ---

def enregistrer_candidat(prenom, nom, date_naissance, lieu_naissance, nationalite, nin, statut, motif_rejet=None, campagne_id=None):
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    try:
        curseur.execute('''
            INSERT INTO candidats (prenom, nom, date_naissance, lieu_naissance, nationalite, nin, statut, motif_rejet, campagne_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (prenom, nom, date_naissance, lieu_naissance, nationalite, nin, statut, motif_rejet, campagne_id))
        
        candidat_id = curseur.lastrowid
        connexion.commit()
        return True, "Candidat enregistré avec succès dans la base de données de la session actuelle.", candidat_id
    except sqlite3.IntegrityError:
        return False, f"Erreur : Le candidat au NIN {nin} a déjà soumis un dossier.", None
    finally:
        connexion.close()

def enregistrer_parrainages_utilises(nins, candidat_id):
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    try:
        # Optimisation : insertion en bloc
        valeurs = [(nin, candidat_id) for nin in nins]
        curseur.executemany("INSERT OR IGNORE INTO parrainages_utilises (nin, candidat_id) VALUES (?, ?)", valeurs)
        connexion.commit()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des parrainages : {e}")
    finally:
        connexion.close()

def recuperer_nins_utilises():
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    curseur.execute("SELECT nin FROM parrainages_utilises")
    nins_utilises = {ligne[0] for ligne in curseur.fetchall()}
    
    connexion.close()
    return nins_utilises

def recuperer_tous_les_candidats(campagne_id=None):
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    if campagne_id:
        curseur.execute('''
            SELECT id, prenom, nom, date_naissance, lieu_naissance, nationalite, nin, statut, motif_rejet, date_soumission 
            FROM candidats WHERE campagne_id = ? ORDER BY date_soumission DESC
        ''', (campagne_id,))
    else:
        curseur.execute('''
            SELECT id, prenom, nom, date_naissance, lieu_naissance, nationalite, nin, statut, motif_rejet, date_soumission 
            FROM candidats ORDER BY date_soumission DESC
        ''')
        
    colonnes = [desc[0] for desc in curseur.description]
    resultats = [dict(zip(colonnes, ligne)) for ligne in curseur.fetchall()]
    
    connexion.close()
    return resultats

def recuperer_statistiques(campagne_id=None):
    connexion = obtenir_connexion()
    curseur = connexion.cursor()
    
    if campagne_id:
        filtre = f"WHERE campagne_id = {campagne_id}"
    else:
        filtre = ""
        
    curseur.execute(f"SELECT COUNT(*) FROM candidats {filtre}")
    total = curseur.fetchone()[0]
    
    curseur.execute(f"SELECT COUNT(*) FROM candidats {filtre} {'AND' if campagne_id else 'WHERE'} statut = 'Acceptée'")
    acceptees = curseur.fetchone()[0]
    
    curseur.execute(f"SELECT COUNT(*) FROM candidats {filtre} {'AND' if campagne_id else 'WHERE'} statut = 'Rejetée'")
    rejetees = curseur.fetchone()[0]
    
    connexion.close()
    
    return {
        "total": total,
        "acceptees": acceptees,
        "rejetees": rejetees
    }

# Initialisation
initialiser_base_de_donnees()
