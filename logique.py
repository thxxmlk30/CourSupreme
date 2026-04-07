from datetime import datetime
import pandas as pd

DATE_ELECTION = datetime(2026, 2, 25)

def verifier_age(date_naissance_str):
    """
    Vérifie si le candidat a plus de 35 ans à la date de l'élection.
    Format attendu : JJ/MM/AAAA
    """
    try:
        date_naissance = datetime.strptime(date_naissance_str, "%d/%m/%Y")
        age = DATE_ELECTION.year - date_naissance.year - ((DATE_ELECTION.month, DATE_ELECTION.day) < (date_naissance.month, date_naissance.day))
        return age > 35, age
    except ValueError:
        return False, -1

def verifier_nationalite(nationalite):
    """
    Vérifie si la nationalité renseignée est sénégalaise.
    """
    nationalite_clean = nationalite.strip().lower()
    mots_clefs = ['sénégalaise', 'senegalaise', 'senegalais', 'sénégalais', 'senegal', 'sénégal']
    if nationalite_clean in mots_clefs:
        return True
    return False

def valider_parrainages(chemin_fichier_parrainages, chemin_fichier_electoral, campagne_id=None):
    """
    Vérifie les parrainages en les croisant avec le fichier électoral.
    Critère: entre 0.8% et 1% du fichier électoral.
    Vérifie également que les parrainages n'ont pas déjà été utilisés.
    """
    if not chemin_fichier_electoral or not chemin_fichier_parrainages:
        return False, "Les fichiers électoral et de parrainage doivent être fournis."

    try:
        df_electoral = pd.read_excel(chemin_fichier_electoral)
        total_inscrits = len(df_electoral)
    except Exception as e:
        return False, f"Impossible de lire le fichier électoral: {str(e)}"

    try:
        df_parrainages = pd.read_excel(chemin_fichier_parrainages)
    except Exception as e:
        return False, f"Impossible de lire le fichier de parrainages: {str(e)}"
    
    try:
        # On convertit les NINs en chaines de caractères pour éviter les soucis de format scientifique
        nins_electoraux = set(df_electoral['Numéro d\'identification nationale'].astype(str))
        nins_parrainages = df_parrainages['Numéro d\'identification nationale'].astype(str).tolist()
    except KeyError:
        return False, "Un des fichiers ne contient pas la colonne 'Numéro d'identification nationale'."

    # Vérifier que les parrainages sont dans la liste électorale
    parrainages_valides = []
    parrainages_invalides = []
    
    for nin in nins_parrainages:
        if nin in nins_electoraux:
            parrainages_valides.append(nin)
        else:
            parrainages_invalides.append(nin)
    
    # Vérifier que les parrainages n'ont pas déjà été utilisés
    parrainages_deja_utilises = []
    if campagne_id:
        from base_donnees import verifier_parrainage_deja_utilise
        for nin in parrainages_valides:
            if verifier_parrainage_deja_utilise(nin, campagne_id):
                parrainages_deja_utilises.append(nin)
                parrainages_valides.remove(nin)
    
    # Calcul des statistiques
    nombre_parrains_valides = len(parrainages_valides)
    nombre_parrains_invalides = len(parrainages_invalides)
    nombre_parrains_deja_utilises = len(parrainages_deja_utilises)
    
    # Seuils calculés
    minimum_requis = int(total_inscrits * 0.008)  # 0.8%
    maximum_autorise = int(total_inscrits * 0.01)    # 1.0%
    
    pourcentage = (nombre_parrains_valides / total_inscrits) * 100
    
    # Construction du message de résultat
    message = ""
    
    if nombre_parrains_invalides > 0:
        message += f"{nombre_parrains_invalides} parrain(s) non trouvés dans la liste électorale. "
    
    if nombre_parrains_deja_utilises > 0:
        message += f"{nombre_parrains_deja_utilises} parrain(s) déjà utilisés par d'autres candidats. "
    
    if nombre_parrains_valides < minimum_requis:
        return False, f"Nombre de parrainages valide insuffisant ({nombre_parrains_valides}/{total_inscrits} soit {pourcentage:.2f}%). Le minimum requis est de 0.8%. {message}"
    elif nombre_parrains_valides > maximum_autorise:
        return False, f"Nombre de parrainages valide excessif ({nombre_parrains_valides}/{total_inscrits} soit {pourcentage:.2f}%). Le maximum autorisé est de 1%. {message}"
    else:
        return True, f"Parrainages validés avec succès : {nombre_parrains_valides}/{total_inscrits} ({pourcentage:.2f}%). {message}"

def arbitrer_candidature(donnees_candidat, chemin_fichier_parrainages, chemin_fichier_electoral, campagne_id=None):
    """
    Applique l'ensemble des règles de la Cour Suprême.
    Retourne un tuple : (est_acceptee: bool, motif_rejet: str ou None, parrainages_valides: list[str])
    """
    # 1. Âge
    est_age_valide, age = verifier_age(donnees_candidat['date_naissance'])
    if not est_age_valide:
        if age == -1:
            return False, "Le format de la date de naissance est invalide (attendu: JJ/MM/AAAA).", []
        return False, f"Âge insuffisant : {age} ans. (Âge minimum requis : 35 ans révolus).", []
        
    # 2. Nationalité
    if not verifier_nationalite(donnees_candidat['nationalite']):
        return False, f"Nationalité invalide : '{donnees_candidat['nationalite']}'. (Nationalité sénégalaise requise).", []
        
    # 3. Parrainages
    est_parrainage_valide, message = valider_parrainages(chemin_fichier_parrainages, chemin_fichier_electoral, campagne_id)
    if not est_parrainage_valide:
        return False, f"Rejet lié aux parrainages : {message}", []
        
    # Récupérer les NINs des parrainages valides pour enregistrement
    try:
        import pandas as pd
        df_parrainages = pd.read_excel(chemin_fichier_parrainages)
        nins_parrainages = df_parrainages['Numéro d\'identification nationale'].astype(str).tolist()
        
        # Filtrer les parrainages valides (dans la liste électorale)
        df_electoral = pd.read_excel(chemin_fichier_electoral)
        nins_electoraux = set(df_electoral['Numéro d\'identification nationale'].astype(str))
        parrainages_valides = [nin for nin in nins_parrainages if nin in nins_electoraux]
        
        # Exclure les parrainages déjà utilisés
        if campagne_id:
            from base_donnees import verifier_parrainage_deja_utilise
            parrainages_valides = [nin for nin in parrainages_valides if not verifier_parrainage_deja_utilise(nin, campagne_id)]
            
    except Exception as e:
        parrainages_valides = []
        
    return True, None, parrainages_valides
